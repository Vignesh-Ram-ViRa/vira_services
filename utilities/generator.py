#!/usr/bin/env python3
"""
Vira Services Code Generator

This utility generates complete Spring Boot services with CRUD operations,
tests, database migrations, and React integration files based on JSON configuration.

Author: Vira Code Generator
Version: 1.0.0
"""

import os
import sys
import json
import logging
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import traceback

# Third-party imports
try:
    import click
    from jinja2 import Environment, FileSystemLoader, Template
    from jsonschema import validate, ValidationError
    import colorlog
    from tqdm import tqdm
except ImportError as e:
    print(f"ERROR: Missing required dependency: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


class ViraCodeGenerator:
    """
    Main code generator class that handles the complete generation process.
    
    This class is responsible for:
    - Loading and validating configuration
    - Processing service definitions
    - Generating all code files (Java, SQL, React)
    - Managing rollback operations
    - Logging all operations
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the code generator with configuration.
        
        Args:
            config_path (str): Path to the configuration JSON file
        """
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.service_definition = None
        self.generated_files = []  # Track files for rollback
        self.backup_directory = None
        self.jinja_env = None
        self.migration_version = None
        
        # Initialize the generator
        self._setup_logging()
        self._load_configuration()
        self._setup_jinja_environment()
        self._create_directories()
    
    def _setup_logging(self) -> None:
        """
        Set up comprehensive logging with both file and console output.
        Uses colored console output for better readability.
        """
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("ViraCodeGenerator")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            log_dir / f"generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info("🚀 Vira Code Generator started")
        self.logger.info(f"📝 Logging to: {file_handler.baseFilename}")
    
    def _load_configuration(self) -> None:
        """
        Load and validate the configuration file.
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
            ValueError: If required configuration keys are missing
        """
        try:
            self.logger.info(f"📖 Loading configuration from: {self.config_path}")
            
            if not Path(self.config_path).exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
            
            # Validate required configuration sections
            required_sections = ['paths', 'generation', 'logging']
            for section in required_sections:
                if section not in self.config:
                    raise ValueError(f"Required configuration section missing: {section}")
            
            # Validate paths exist
            vira_root = Path(self.config['paths']['vira_services_root'])
            if not vira_root.exists():
                raise ValueError(f"Vira services root directory doesn't exist: {vira_root}")
            
            self.logger.info("✅ Configuration loaded successfully")
            self.logger.debug(f"Configuration: {json.dumps(self.config, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {str(e)}")
            raise
    
    def _setup_jinja_environment(self) -> None:
        """
        Set up Jinja2 template environment for code generation.
        """
        try:
            self.logger.info("🎨 Setting up Jinja2 template environment")
            
            # Create templates directory if it doesn't exist
            templates_dir = Path("templates")
            templates_dir.mkdir(exist_ok=True)
            
            # Set up Jinja2 environment
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )
            
            # Add custom filters for code generation
            self.jinja_env.filters['camelCase'] = self._to_camel_case
            self.jinja_env.filters['pascalCase'] = self._to_pascal_case
            self.jinja_env.filters['snakeCase'] = self._to_snake_case
            self.jinja_env.filters['sanitize'] = self._sanitize_string
            self.jinja_env.filters['javaType'] = self._get_java_type
            
            self.logger.info("✅ Jinja2 environment configured successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Jinja2 environment: {str(e)}")
            raise
    
    def _create_directories(self) -> None:
        """
        Create necessary directories for generation and backups.
        """
        try:
            self.logger.info("📁 Creating necessary directories")
            
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.backup_directory = Path(f"backups/backup_{timestamp}")
            self.backup_directory.mkdir(parents=True, exist_ok=True)
            
            # Create output directories
            output_dirs = [
                "logs",
                "backups",
                "templates",
                "examples"
            ]
            
            for dir_name in output_dirs:
                Path(dir_name).mkdir(exist_ok=True)
            
            self.logger.info(f"✅ Directories created. Backup location: {self.backup_directory}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create directories: {str(e)}")
            raise
    
    def load_service_definition(self, definition_path: str) -> None:
        """
        Load and validate the service definition JSON file.
        
        Args:
            definition_path (str): Path to the service definition file
            
        Raises:
            FileNotFoundError: If definition file doesn't exist
            ValidationError: If definition doesn't match schema
        """
        try:
            self.logger.info(f"📖 Loading service definition from: {definition_path}")
            
            if not Path(definition_path).exists():
                raise FileNotFoundError(f"Service definition file not found: {definition_path}")
            
            with open(definition_path, 'r', encoding='utf-8') as file:
                self.service_definition = json.load(file)
            
            # Validate the service definition
            self._validate_service_definition()
            
            self.logger.info("✅ Service definition loaded and validated successfully")
            self.logger.info(f"🏷️  Service: {self.service_definition['service']['name']}")
            self.logger.info(f"📊 Table: {self.service_definition['database']['table']}")
            self.logger.info(f"🔢 Fields: {len(self.service_definition['fields'])}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load service definition: {str(e)}")
            raise
    
    def _validate_service_definition(self) -> None:
        """
        Validate the service definition against our schema.
        Performs comprehensive validation including naming conventions and security.
        """
        try:
            self.logger.info("🔍 Validating service definition")
            
            # Basic structure validation
            required_sections = ['service', 'database', 'fields', 'operations', 'api']
            for section in required_sections:
                if section not in self.service_definition:
                    raise ValueError(f"Required section missing: {section}")
            
            # Validate service name (alphanumeric, no spaces)
            service_name = self.service_definition['service']['name']
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', service_name):
                raise ValueError(f"Invalid service name: {service_name}. Must be alphanumeric, start with letter.")
            
            # Validate table name follows convention
            table_name = self.service_definition['database']['table']
            if not re.match(r'^[a-z][a-z0-9_]*$', table_name):
                raise ValueError(f"Invalid table name: {table_name}. Must be lowercase with underscores.")
            
            # Validate fields
            fields = self.service_definition['fields']
            if not fields or len(fields) == 0:
                raise ValueError("At least one field is required")
            
            # Check for primary key
            has_primary_key = any(field.get('primaryKey', False) for field in fields)
            if not has_primary_key:
                raise ValueError("At least one field must be marked as primaryKey")
            
            # Validate field names and types
            for field in fields:
                field_name = field.get('name', '')
                if not re.match(r'^[a-z][a-z0-9_]*$', field_name):
                    raise ValueError(f"Invalid field name: {field_name}. Must be lowercase with underscores.")
                
                if 'type' not in field or 'javaType' not in field:
                    raise ValueError(f"Field {field_name} must have both 'type' and 'javaType'")
                
                # Security validation - check for potentially dangerous content
                if 'validation' in field and 'sanitize' in field['validation']:
                    self.logger.info(f"🔒 Field {field_name} will be sanitized for security")
            
            # Validate API endpoints
            if 'endpoints' in self.service_definition['api']:
                for endpoint in self.service_definition['api']['endpoints']:
                    if 'method' not in endpoint or 'path' not in endpoint:
                        raise ValueError("Each endpoint must have 'method' and 'path'")
            
            self.logger.info("✅ Service definition validation passed")
            
        except Exception as e:
            self.logger.error(f"❌ Service definition validation failed: {str(e)}")
            raise
    
    def generate_code(self) -> bool:
        """
        Generate all code files based on the service definition.
        
        Returns:
            bool: True if generation successful, False otherwise
        """
        try:
            self.logger.info("🚀 Starting code generation process")
            
            # Get next migration version
            self._determine_migration_version()
            
            # Generate files in order
            generation_steps = [
                ("📊 Generating database migration", self._generate_migration),
                ("🏗️  Generating model class", self._generate_model),
                ("🗃️  Generating repository interface", self._generate_repository),
                ("⚙️  Generating service class", self._generate_service),
                ("🌐 Generating controller class", self._generate_controller),
                ("📥 Generating request DTO", self._generate_request_dto),
                ("📤 Generating response DTO", self._generate_response_dto),
                ("🧪 Generating test classes", self._generate_tests),
                ("⚛️  Generating React integration", self._generate_react_integration)
            ]
            
            # Execute generation steps with progress bar
            with tqdm(total=len(generation_steps), desc="Generating code") as pbar:
                for step_desc, step_func in generation_steps:
                    self.logger.info(step_desc)
                    step_func()
                    pbar.update(1)
            
            self.logger.info("✅ Code generation completed successfully")
            self.logger.info(f"📁 Generated {len(self.generated_files)} files")
            
            # Print summary
            self._print_generation_summary()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Code generation failed: {str(e)}")
            self.logger.error(f"🔄 Rolling back changes...")
            self._rollback_changes()
            return False
    
    def _determine_migration_version(self) -> None:
        """
        Determine the next migration version number by checking existing migrations.
        """
        try:
            migration_path = Path(self.config['paths']['migration_path'])
            
            if not migration_path.exists():
                self.migration_version = "V1"
                self.logger.info(f"📊 Migration directory doesn't exist. Using version: {self.migration_version}")
                return
            
            # Find existing migration files
            migration_files = list(migration_path.glob("V*.sql"))
            
            if not migration_files:
                self.migration_version = "V1"
                self.logger.info(f"📊 No existing migrations found. Using version: {self.migration_version}")
                return
            
            # Extract version numbers and find the highest
            version_numbers = []
            for file in migration_files:
                match = re.match(r'V(\d+)__.*\.sql', file.name)
                if match:
                    version_numbers.append(int(match.group(1)))
            
            if version_numbers:
                next_version = max(version_numbers) + 1
                self.migration_version = f"V{next_version}"
            else:
                self.migration_version = "V1"
            
            self.logger.info(f"📊 Determined next migration version: {self.migration_version}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to determine migration version: {str(e)}")
            self.migration_version = "V1"  # Fallback
    
    def _generate_migration(self) -> None:
        """Generate database migration SQL file."""
        # This will be implemented with the SQL template
        pass
    
    def _generate_model(self) -> None:
        """Generate JPA entity model class."""
        # This will be implemented with the model template
        pass
    
    def _generate_repository(self) -> None:
        """Generate Spring Data JPA repository interface."""
        # This will be implemented with the repository template
        pass
    
    def _generate_service(self) -> None:
        """Generate service class with business logic."""
        # This will be implemented with the service template
        pass
    
    def _generate_controller(self) -> None:
        """Generate REST controller class."""
        # This will be implemented with the controller template
        pass
    
    def _generate_request_dto(self) -> None:
        """Generate request DTO class."""
        # This will be implemented with the request DTO template
        pass
    
    def _generate_response_dto(self) -> None:
        """Generate response DTO class."""
        # This will be implemented with the response DTO template
        pass
    
    def _generate_tests(self) -> None:
        """Generate comprehensive test classes."""
        # This will be implemented with test templates
        pass
    
    def _generate_react_integration(self) -> None:
        """Generate React API service and TypeScript definitions."""
        # This will be implemented with React templates
        pass
    
    def _rollback_changes(self) -> None:
        """
        Rollback all generated files in case of failure.
        """
        try:
            self.logger.info("🔄 Starting rollback process")
            
            for file_path in reversed(self.generated_files):
                if Path(file_path).exists():
                    Path(file_path).unlink()
                    self.logger.info(f"🗑️  Removed: {file_path}")
            
            self.logger.info("✅ Rollback completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {str(e)}")
    
    def _print_generation_summary(self) -> None:
        """Print a summary of generated files."""
        self.logger.info("\n" + "="*50)
        self.logger.info("📋 GENERATION SUMMARY")
        self.logger.info("="*50)
        
        for file_path in self.generated_files:
            self.logger.info(f"✅ {file_path}")
        
        self.logger.info("="*50)
        self.logger.info(f"🎉 Successfully generated {len(self.generated_files)} files")
        self.logger.info("🚀 Ready for deployment!")
    
    # Utility methods for template filters
    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])
    
    @staticmethod
    def _to_pascal_case(snake_str: str) -> str:
        """Convert snake_case to PascalCase."""
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
    
    @staticmethod
    def _to_snake_case(camel_str: str) -> str:
        """Convert camelCase/PascalCase to snake_case."""
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', camel_str).lower()
    
    @staticmethod
    def _sanitize_string(value: str) -> str:
        """Sanitize string for security (basic implementation)."""
        if not isinstance(value, str):
            return str(value)
        # Remove potentially dangerous characters
        return re.sub(r'[<>&"\']', '', value)
    
    @staticmethod
    def _get_java_type(sql_type: str) -> str:
        """Map SQL types to Java types."""
        type_mapping = {
            'BIGSERIAL': 'Long',
            'BIGINT': 'Long',
            'INTEGER': 'Integer',
            'DECIMAL': 'BigDecimal',
            'VARCHAR': 'String',
            'TEXT': 'String',
            'TIMESTAMP': 'LocalDateTime',
            'DATE': 'LocalDate',
            'BOOLEAN': 'Boolean'
        }
        
        # Extract base type (remove precision/scale)
        base_type = sql_type.split('(')[0].upper()
        return type_mapping.get(base_type, 'String')


def detect_operation_type(definition_file: str) -> str:
    """
    Detect the operation type from the definition file.
    
    Args:
        definition_file: Path to the definition file
        
    Returns:
        Operation type: 'create_service' or 'modify_service'
    """
    try:
        with open(definition_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('operation_type', 'create_service')
    except Exception:
        return 'create_service'  # Default to create service


@click.command()
@click.option('--config', '-c', default='config.json', help='Configuration file path')
@click.option('--definition', '-d', default='service_definition.json', help='Service definition file path')
@click.option('--operation', '-o', help='Operation type: create_service or modify_service (auto-detected if not specified)')
@click.option('--dry-run', is_flag=True, help='Show what would be changed without applying')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(config: str, definition: str, operation: str, dry_run: bool, verbose: bool):
    """
    Vira Services Code Generator
    
    Generate complete Spring Boot services with CRUD operations, tests, and React integration.
    Also supports field modification operations for existing services.
    """
    try:
        # Detect operation type if not specified
        if not operation:
            operation = detect_operation_type(definition)
        
        if operation == 'modify_service':
            # Import field modifier (lazy import to avoid circular dependencies)
            from field_modifier import FieldModifier
            
            # Create field modifier
            modifier = FieldModifier(config)
            
            # Set verbose logging if requested
            if verbose:
                modifier.logger.setLevel(logging.DEBUG)
            
            # Override dry-run if specified
            if dry_run:
                with open(definition, 'r') as f:
                    ops_data = json.load(f)
                ops_data.setdefault('options', {})['dry_run'] = True
                
                temp_file = definition + ".tmp"
                with open(temp_file, 'w') as f:
                    json.dump(ops_data, f, indent=2)
                
                definition = temp_file
            
            # Process field operations
            success = modifier.process_field_operations(definition)
            
            # Clean up temp file
            if dry_run and definition.endswith('.tmp'):
                Path(definition).unlink()
            
            if success:
                print("\n🎉 Field modification completed successfully!")
                print("🚀 Your service modifications are ready!")
                sys.exit(0)
            else:
                print("\n❌ Field modification failed. Check logs for details.")
                sys.exit(1)
        
        else:
            # Create generator instance for service creation
            generator = ViraCodeGenerator(config)
            
            # Set verbose logging if requested
            if verbose:
                generator.logger.setLevel(logging.DEBUG)
            
            # Load service definition
            generator.load_service_definition(definition)
            
            # Generate code
            success = generator.generate_code()
            
            if success:
                print("\n🎉 Code generation completed successfully!")
                print("🚀 Your service is ready for deployment!")
                sys.exit(0)
            else:
                print("\n❌ Code generation failed. Check logs for details.")
                sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        print(f"📝 Check logs for detailed information.")
        sys.exit(1)


if __name__ == "__main__":
    main() 