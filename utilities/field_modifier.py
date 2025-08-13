#!/usr/bin/env python3
"""
Vira Services Field Modifier

This module provides field management capabilities for existing services:
- Add new fields to existing tables/entities
- Update existing field properties
- Remove deprecated fields
- Validate operations for safety
- Backup and rollback functionality

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
from typing import Dict, List, Any, Optional, Tuple, Set
import traceback

try:
    import click
    from jinja2 import Environment, FileSystemLoader, Template
    import colorlog
except ImportError as e:
    print(f"ERROR: Missing required dependency: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


class FieldOperation:
    """Represents a single field operation (add/update/remove)."""
    
    def __init__(self, action: str, field_data: Dict[str, Any]):
        self.action = action.lower()
        self.field_data = field_data
        self.validate()
    
    def validate(self):
        """Validate the field operation."""
        valid_actions = ['add', 'update', 'remove']
        if self.action not in valid_actions:
            raise ValueError(f"Invalid action: {self.action}. Must be one of {valid_actions}")
        
        if self.action == 'add':
            required_fields = ['name', 'type', 'javaType']
            if not all(field in self.field_data.get('field', {}) for field in required_fields):
                raise ValueError(f"Add operation requires: {required_fields}")
        
        elif self.action == 'update':
            if 'field_name' not in self.field_data:
                raise ValueError("Update operation requires 'field_name'")
            if 'changes' not in self.field_data:
                raise ValueError("Update operation requires 'changes'")
        
        elif self.action == 'remove':
            if 'field_name' not in self.field_data:
                raise ValueError("Remove operation requires 'field_name'")


class ImpactAnalyzer:
    """Analyzes the impact of field operations on the codebase."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def analyze_field_operations(self, service_info: Dict, operations: List[FieldOperation]) -> Dict[str, Any]:
        """
        Analyze the impact of field operations.
        
        Args:
            service_info: Information about the target service
            operations: List of field operations to analyze
            
        Returns:
            Impact analysis report
        """
        self.logger.info(f"Analyzing impact of {len(operations)} field operations")
        
        analysis = {
            "service_name": service_info['name'],
            "table_name": service_info['table'],
            "operations_count": len(operations),
            "files_to_modify": [],
            "migration_changes": [],
            "potential_risks": [],
            "dependency_impacts": [],
            "breaking_changes": [],
            "validation_results": []
        }
        
        for operation in operations:
            self._analyze_single_operation(analysis, service_info, operation)
        
        # Determine files that will be modified
        analysis["files_to_modify"] = self._get_affected_files(service_info)
        
        return analysis
    
    def _analyze_single_operation(self, analysis: Dict, service_info: Dict, operation: FieldOperation):
        """Analyze a single field operation."""
        if operation.action == 'add':
            field = operation.field_data['field']
            analysis["migration_changes"].append({
                "type": "ADD_COLUMN",
                "field_name": field['name'],
                "sql": f"ALTER TABLE {service_info['table']} ADD COLUMN {field['name']} {field['type']}"
            })
            
            if not field.get('nullable', True) and 'default_value' not in field:
                analysis["potential_risks"].append(
                    f"Adding non-nullable field '{field['name']}' without default value may fail if table has data"
                )
        
        elif operation.action == 'update':
            field_name = operation.field_data['field_name']
            changes = operation.field_data['changes']
            
            if 'type' in changes:
                analysis["migration_changes"].append({
                    "type": "MODIFY_COLUMN",
                    "field_name": field_name,
                    "sql": f"ALTER TABLE {service_info['table']} ALTER COLUMN {field_name} TYPE {changes['type']}"
                })
                
                analysis["potential_risks"].append(
                    f"Changing type of field '{field_name}' may cause data loss if incompatible"
                )
        
        elif operation.action == 'remove':
            field_name = operation.field_data['field_name']
            analysis["migration_changes"].append({
                "type": "DROP_COLUMN",
                "field_name": field_name,
                "sql": f"-- ALTER TABLE {service_info['table']} DROP COLUMN {field_name}; -- REQUIRES MANUAL CONFIRMATION"
            })
            
            analysis["breaking_changes"].append(
                f"Removing field '{field_name}' will break any code that references it"
            )
    
    def _get_affected_files(self, service_info: Dict) -> List[str]:
        """Get list of files that will be affected by field operations."""
        service_name = service_info['name']
        entity_name = service_info.get('entity', service_name.capitalize())
        
        return [
            f"src/main/java/com/vira/{service_name}/model/{entity_name}.java",
            f"src/main/java/com/vira/{service_name}/dto/{entity_name}Request.java",
            f"src/main/java/com/vira/{service_name}/dto/{entity_name}Response.java",
            f"src/main/java/com/vira/{service_name}/service/{entity_name}Service.java",
            f"src/main/java/com/vira/{service_name}/repository/{entity_name}Repository.java",
            f"src/main/java/com/vira/{service_name}/controller/{entity_name}Controller.java",
            f"src/test/java/com/vira/{service_name}/service/{entity_name}ServiceTest.java",
            f"src/test/java/com/vira/{service_name}/controller/{entity_name}ControllerTest.java",
            f"src/main/resources/frontend/api/{entity_name.lower()}ApiService.js"
        ]


class BackupManager:
    """Manages backup and restore operations for field modifications."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.backup_base_dir = Path("backups")
        self.backup_base_dir.mkdir(exist_ok=True)
    
    def create_backup(self, service_name: str, project_root: Path) -> str:
        """
        Create a backup of all files that will be modified.
        
        Args:
            service_name: Name of the service being modified
            project_root: Root path of the Vira Services project
            
        Returns:
            Backup ID for later restoration
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"field_modification_{service_name}_{timestamp}"
        backup_dir = self.backup_base_dir / backup_id
        
        self.logger.info(f"Creating backup: {backup_id}")
        
        try:
            backup_dir.mkdir(parents=True)
            
            # Files to backup based on service structure
            files_to_backup = [
                f"src/main/java/com/vira/{service_name}",
                f"src/test/java/com/vira/{service_name}",
                f"src/main/resources/frontend/api",
                "src/main/resources/db/migration"
            ]
            
            for file_path in files_to_backup:
                source_path = project_root / file_path
                if source_path.exists():
                    if source_path.is_dir():
                        dest_path = backup_dir / file_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    else:
                        dest_path = backup_dir / file_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
            
            # Create backup manifest
            manifest = {
                "backup_id": backup_id,
                "service_name": service_name,
                "timestamp": timestamp,
                "files_backed_up": files_to_backup,
                "project_root": str(project_root)
            }
            
            with open(backup_dir / "manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self.logger.info(f"✅ Backup created successfully: {backup_id}")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create backup: {str(e)}")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            raise
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore files from a backup.
        
        Args:
            backup_id: ID of the backup to restore
            
        Returns:
            True if restoration successful, False otherwise
        """
        backup_dir = self.backup_base_dir / backup_id
        
        if not backup_dir.exists():
            self.logger.error(f"❌ Backup not found: {backup_id}")
            return False
        
        try:
            # Load backup manifest
            with open(backup_dir / "manifest.json", 'r') as f:
                manifest = json.load(f)
            
            project_root = Path(manifest['project_root'])
            self.logger.info(f"🔄 Restoring backup: {backup_id}")
            
            for file_path in manifest['files_backed_up']:
                backup_file = backup_dir / file_path
                target_file = project_root / file_path
                
                if backup_file.exists():
                    if backup_file.is_dir():
                        if target_file.exists():
                            shutil.rmtree(target_file)
                        shutil.copytree(backup_file, target_file)
                    else:
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(backup_file, target_file)
            
            self.logger.info(f"✅ Backup restored successfully: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restore backup: {str(e)}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for backup_dir in self.backup_base_dir.iterdir():
            if backup_dir.is_dir():
                manifest_file = backup_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest = json.load(f)
                        backups.append(manifest)
                    except Exception:
                        continue
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)


class DependencyChecker:
    """Checks for dependencies and references to fields being modified."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def check_field_usage(self, service_name: str, field_name: str, project_root: Path) -> Dict[str, List[str]]:
        """
        Check where a field is used across the codebase.
        
        Args:
            service_name: Name of the service
            field_name: Name of the field to check
            project_root: Root path of the project
            
        Returns:
            Dictionary with usage locations
        """
        self.logger.info(f"🔍 Checking usage of field '{field_name}' in service '{service_name}'")
        
        usage = {
            "java_files": [],
            "test_files": [],
            "frontend_files": [],
            "migration_files": [],
            "potential_issues": []
        }
        
        # Convert field name to different naming conventions
        camel_case = self._to_camel_case(field_name)
        pascal_case = self._to_pascal_case(field_name)
        
        search_patterns = [field_name, camel_case, pascal_case]
        
        # Search in Java files
        java_dir = project_root / "src" / "main" / "java" / "com" / "vira" / service_name
        if java_dir.exists():
            usage["java_files"] = self._search_in_directory(java_dir, search_patterns, [".java"])
        
        # Search in test files
        test_dir = project_root / "src" / "test" / "java" / "com" / "vira" / service_name
        if test_dir.exists():
            usage["test_files"] = self._search_in_directory(test_dir, search_patterns, [".java"])
        
        # Search in frontend files
        frontend_dir = project_root / "src" / "main" / "resources" / "frontend"
        if frontend_dir.exists():
            usage["frontend_files"] = self._search_in_directory(frontend_dir, search_patterns, [".js", ".ts"])
        
        # Search in migration files
        migration_dir = project_root / "src" / "main" / "resources" / "db" / "migration"
        if migration_dir.exists():
            usage["migration_files"] = self._search_in_directory(migration_dir, [field_name], [".sql"])
        
        return usage
    
    def validate_operation_safety(self, operation: FieldOperation, service_info: Dict, project_root: Path) -> List[str]:
        """
        Validate if an operation is safe to perform.
        
        Args:
            operation: The field operation to validate
            service_info: Information about the service
            project_root: Root path of the project
            
        Returns:
            List of validation errors (empty if safe)
        """
        errors = []
        
        if operation.action == 'remove':
            field_name = operation.field_data['field_name']
            
            # Check if field is a primary key
            if self._is_primary_key(field_name, service_info, project_root):
                errors.append(f"Cannot remove primary key field: {field_name}")
            
            # Check if field is referenced by foreign keys
            if self._has_foreign_key_references(field_name, service_info, project_root):
                errors.append(f"Field {field_name} is referenced by foreign keys in other tables")
        
        elif operation.action == 'update':
            field_name = operation.field_data['field_name']
            changes = operation.field_data['changes']
            
            # Check if trying to modify primary key
            if self._is_primary_key(field_name, service_info, project_root):
                errors.append(f"Cannot modify primary key field: {field_name}")
            
            # Check type compatibility
            if 'type' in changes:
                if not self._is_type_change_safe(field_name, changes['type'], service_info, project_root):
                    errors.append(f"Type change for field {field_name} may cause data loss")
        
        return errors
    
    def _search_in_directory(self, directory: Path, patterns: List[str], extensions: List[str]) -> List[str]:
        """Search for patterns in files within a directory."""
        matches = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in patterns:
                            if pattern in content:
                                relative_path = file_path.relative_to(directory.parent.parent.parent.parent)
                                matches.append(str(relative_path))
                                break
                except Exception:
                    continue
        
        return matches
    
    def _is_primary_key(self, field_name: str, service_info: Dict, project_root: Path) -> bool:
        """Check if a field is a primary key."""
        # This is a simplified check - in a real implementation, 
        # you might parse the actual model file or check database schema
        return field_name.lower() in ['id', 'uuid']
    
    def _has_foreign_key_references(self, field_name: str, service_info: Dict, project_root: Path) -> bool:
        """Check if field has foreign key references."""
        # Simplified check - scan migration files for references
        migration_dir = project_root / "src" / "main" / "resources" / "db" / "migration"
        if not migration_dir.exists():
            return False
        
        table_name = service_info['table']
        reference_pattern = f"REFERENCES {table_name}({field_name})"
        
        for migration_file in migration_dir.glob("*.sql"):
            try:
                with open(migration_file, 'r') as f:
                    content = f.read()
                    if reference_pattern in content:
                        return True
            except Exception:
                continue
        
        return False
    
    def _is_type_change_safe(self, field_name: str, new_type: str, service_info: Dict, project_root: Path) -> bool:
        """Check if a type change is safe (simplified implementation)."""
        # This is a basic safety check - expanding string lengths is generally safe
        # Converting between incompatible types (string to number) is not
        if 'VARCHAR' in new_type.upper():
            return True  # VARCHAR changes are generally safe if expanding
        return False  # Conservative approach for other types
    
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


class ConfirmationManager:
    """Manages user confirmation for field operations."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def show_impact_analysis(self, analysis: Dict[str, Any]) -> None:
        """Display detailed impact analysis."""
        print("\n" + "="*60)
        print("🔍 FIELD MODIFICATION IMPACT ANALYSIS")
        print("="*60)
        
        print(f"📊 Service: {analysis['service_name']}")
        print(f"📊 Table: {analysis['table_name']}")
        print(f"📊 Operations: {analysis['operations_count']}")
        
        if analysis['migration_changes']:
            print(f"\n📝 DATABASE CHANGES ({len(analysis['migration_changes'])}):")
            for change in analysis['migration_changes']:
                print(f"  • {change['type']}: {change['field_name']}")
                print(f"    SQL: {change['sql']}")
        
        if analysis['files_to_modify']:
            print(f"\n📁 FILES TO MODIFY ({len(analysis['files_to_modify'])}):")
            for file_path in analysis['files_to_modify']:
                print(f"  • {file_path}")
        
        if analysis['potential_risks']:
            print(f"\n⚠️  POTENTIAL RISKS ({len(analysis['potential_risks'])}):")
            for risk in analysis['potential_risks']:
                print(f"  • {risk}")
        
        if analysis['breaking_changes']:
            print(f"\n💥 BREAKING CHANGES ({len(analysis['breaking_changes'])}):")
            for change in analysis['breaking_changes']:
                print(f"  • {change}")
        
        print("="*60)
    
    def confirm_operations(self, analysis: Dict[str, Any], has_destructive_ops: bool = False) -> bool:
        """
        Request user confirmation for field operations.
        
        Args:
            analysis: Impact analysis results
            has_destructive_ops: Whether operations include destructive changes
            
        Returns:
            True if user confirms, False otherwise
        """
        self.show_impact_analysis(analysis)
        
        if has_destructive_ops:
            print("\n🚨 WARNING: This operation includes potentially destructive changes!")
            print("   Make sure you have a backup before proceeding.")
        
        print(f"\n🔄 This will modify {len(analysis['files_to_modify'])} files")
        print("   A backup will be created automatically before any changes.")
        
        while True:
            response = input("\n❓ Do you want to proceed? (yes/no/show-details): ").lower().strip()
            
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            elif response in ['show-details', 'details', 'd']:
                self._show_detailed_analysis(analysis)
            else:
                print("   Please enter 'yes', 'no', or 'show-details'")
    
    def _show_detailed_analysis(self, analysis: Dict[str, Any]) -> None:
        """Show detailed analysis information."""
        print("\n📋 DETAILED ANALYSIS:")
        
        if analysis.get('validation_results'):
            print("\n🔍 Validation Results:")
            for result in analysis['validation_results']:
                print(f"  • {result}")
        
        if analysis.get('dependency_impacts'):
            print("\n🔗 Dependency Impacts:")
            for impact in analysis['dependency_impacts']:
                print(f"  • {impact}")


class FieldModifier:
    """Main class for managing field modifications in Vira Services."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the field modifier."""
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.project_root = None
        
        # Initialize components
        self._setup_logging()
        self._load_configuration()
        
        # Initialize managers
        self.impact_analyzer = ImpactAnalyzer(self.logger)
        self.backup_manager = BackupManager(self.logger)
        self.dependency_checker = DependencyChecker(self.logger)
        self.confirmation_manager = ConfirmationManager(self.logger)
    
    def _setup_logging(self) -> None:
        """Set up logging for field modifier."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("FieldModifier")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
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
        
        # File handler
        file_handler = logging.FileHandler(
            log_dir / f"field_modifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info("🔧 Field Modifier initialized")
    
    def _load_configuration(self) -> None:
        """Load configuration from config file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
            
            self.project_root = Path(self.config['paths']['vira_services_root'])
            
            if not self.project_root.exists():
                raise ValueError(f"Project root doesn't exist: {self.project_root}")
            
            self.logger.info("✅ Configuration loaded successfully")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to load configuration: {str(e)}")
            raise
    
    def process_field_operations(self, operations_file: str) -> bool:
        """
        Process field operations from a JSON file.
        
        Args:
            operations_file: Path to the field operations JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"📖 Processing field operations from: {operations_file}")
            
            # Load operations file
            with open(operations_file, 'r', encoding='utf-8') as f:
                operations_data = json.load(f)
            
            # Validate operations file
            self._validate_operations_file(operations_data)
            
            # Parse operations
            service_info = operations_data['target_service']
            field_operations = [FieldOperation(op['action'], op) for op in operations_data['field_operations']]
            options = operations_data.get('options', {})
            
            # Analyze impact
            analysis = self.impact_analyzer.analyze_field_operations(service_info, field_operations)
            
            # Validate operations safety
            validation_errors = []
            for operation in field_operations:
                errors = self.dependency_checker.validate_operation_safety(operation, service_info, self.project_root)
                validation_errors.extend(errors)
            
            if validation_errors:
                self.logger.error("❌ Validation failed:")
                for error in validation_errors:
                    self.logger.error(f"  • {error}")
                return False
            
            # Check if dry run
            if options.get('dry_run', False):
                self.logger.info("🏃 DRY RUN MODE - No changes will be applied")
                self.confirmation_manager.show_impact_analysis(analysis)
                return True
            
            # Get user confirmation
            has_destructive_ops = any(op.action == 'remove' for op in field_operations)
            
            if not options.get('auto_confirm', False):
                if not self.confirmation_manager.confirm_operations(analysis, has_destructive_ops):
                    self.logger.info("❌ Operation cancelled by user")
                    return False
            
            # Create backup
            backup_id = self.backup_manager.create_backup(service_info['name'], self.project_root)
            
            try:
                # Apply field operations
                self._apply_field_operations(service_info, field_operations, analysis)
                
                self.logger.info("✅ Field operations completed successfully")
                self.logger.info(f"💾 Backup available: {backup_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Field operations failed: {str(e)}")
                self.logger.info("🔄 Restoring from backup...")
                
                if self.backup_manager.restore_backup(backup_id):
                    self.logger.info("✅ Successfully restored from backup")
                else:
                    self.logger.error("❌ Failed to restore from backup!")
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to process field operations: {str(e)}")
            return False
    
    def _validate_operations_file(self, data: Dict[str, Any]) -> None:
        """Validate the operations file structure."""
        required_fields = ['operation_type', 'target_service', 'field_operations']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if data['operation_type'] != 'modify_service':
            raise ValueError(f"Invalid operation_type: {data['operation_type']}")
        
        target_service = data['target_service']
        required_service_fields = ['name', 'table']
        
        for field in required_service_fields:
            if field not in target_service:
                raise ValueError(f"Missing required target_service field: {field}")
        
        if not data['field_operations']:
            raise ValueError("No field operations specified")
    
    def _apply_field_operations(self, service_info: Dict, operations: List[FieldOperation], analysis: Dict) -> None:
        """Apply the field operations by generating migration and updating files."""
        self.logger.info("🔧 Applying field operations...")
        
        try:
            # Import file updater
            from file_updater import JavaFileUpdater
            file_updater = JavaFileUpdater(self.logger)
            file_updater.setup_templates()
            
            # 1. Generate migration file
            self._generate_migration_file(service_info, operations, analysis)
            
            # 2. Update model files
            self._update_model_files(service_info, operations, file_updater)
            
            # 3. Update DTO files
            self._update_dto_files(service_info, operations, file_updater)
            
            # 4. Update service files
            self._update_service_files(service_info, operations, file_updater)
            
            # 5. Update repository files
            self._update_repository_files(service_info, operations)
            
            # 6. Update controller files
            self._update_controller_files(service_info, operations)
            
            # 7. Update test files
            self._update_test_files(service_info, operations)
            
            # 8. Generate React files
            self._update_react_files(service_info, operations)
            
            self.logger.info("✅ All field operations applied successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply field operations: {str(e)}")
            raise
    
    def _generate_migration_file(self, service_info: Dict, operations: List[FieldOperation], analysis: Dict) -> None:
        """Generate database migration file for field operations."""
        self.logger.info("📝 Generating migration file...")
        
        try:
            # Determine migration version
            migration_dir = self.project_root / "src" / "main" / "resources" / "db" / "migration"
            migration_dir.mkdir(parents=True, exist_ok=True)
            
            # Find next migration version
            existing_migrations = list(migration_dir.glob("V*.sql"))
            if existing_migrations:
                version_numbers = []
                for migration in existing_migrations:
                    match = re.match(r'V(\d+)__.*\.sql', migration.name)
                    if match:
                        version_numbers.append(int(match.group(1)))
                next_version = max(version_numbers) + 1 if version_numbers else 1
            else:
                next_version = 1
            
            migration_version = f"V{next_version}"
            
            # Categorize operations
            add_operations = [op for op in operations if op.action == "add"]
            update_operations = [op for op in operations if op.action == "update"]
            remove_operations = [op for op in operations if op.action == "remove"]
            
            # Generate operations summary
            op_counts = []
            if add_operations:
                op_counts.append(f"Add {len(add_operations)} field{'s' if len(add_operations) > 1 else ''}")
            if update_operations:
                op_counts.append(f"Update {len(update_operations)} field{'s' if len(update_operations) > 1 else ''}")
            if remove_operations:
                op_counts.append(f"Remove {len(remove_operations)} field{'s' if len(remove_operations) > 1 else ''}")
            
            operations_summary = ", ".join(op_counts)
            
            # Setup Jinja2 environment
            templates_dir = Path("templates/field_operations")
            if templates_dir.exists():
                from jinja2 import Environment, FileSystemLoader
                jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))
                template = jinja_env.get_template("migration_alter.sql.j2")
                
                # Render migration
                migration_content = template.render(
                    migration_version=migration_version,
                    service_name=service_info['name'],
                    table_name=service_info['table'],
                    service_description=service_info.get('description', f"{service_info['name']} service"),
                    operations_summary=operations_summary,
                    generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    add_operations=add_operations,
                    update_operations=update_operations,
                    remove_operations=remove_operations,
                    fields_with_updated_at=any(op.field_data.get("field", {}).get("name") == "updated_at" 
                                             for op in add_operations)
                )
                
                # Write migration file
                migration_filename = f"{migration_version}__Update_{service_info['name']}_{service_info['table']}_fields.sql"
                migration_path = migration_dir / migration_filename
                
                with open(migration_path, 'w', encoding='utf-8') as f:
                    f.write(migration_content)
                
                self.logger.info(f"✅ Migration file generated: {migration_filename}")
            else:
                self.logger.warning("⚠️  Migration template not found, skipping migration generation")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate migration: {str(e)}")
            raise
    
    def _update_model_files(self, service_info: Dict, operations: List[FieldOperation], file_updater) -> None:
        """Update JPA model files."""
        self.logger.info("🏗️  Updating model files...")
        
        entity_name = service_info.get('entity', service_info['name'].capitalize())
        model_path = self.project_root / "src" / "main" / "java" / "com" / "vira" / service_info['name'] / "model" / f"{entity_name}.java"
        
        if model_path.exists():
            success = file_updater.update_model_file(model_path, operations, service_info)
            if success:
                self.logger.info("✅ Model file updated successfully")
            else:
                self.logger.warning("⚠️  Failed to update model file")
        else:
            self.logger.warning(f"⚠️  Model file not found: {model_path}")
    
    def _update_dto_files(self, service_info: Dict, operations: List[FieldOperation], file_updater) -> None:
        """Update DTO files."""
        self.logger.info("📦 Updating DTO files...")
        
        entity_name = service_info.get('entity', service_info['name'].capitalize())
        dto_dir = self.project_root / "src" / "main" / "java" / "com" / "vira" / service_info['name'] / "dto"
        
        request_path = dto_dir / f"{entity_name}Request.java"
        response_path = dto_dir / f"{entity_name}Response.java"
        
        if request_path.exists() or response_path.exists():
            success = file_updater.update_dto_files(request_path, response_path, operations, service_info)
            if success:
                self.logger.info("✅ DTO files updated successfully")
            else:
                self.logger.warning("⚠️  Failed to update DTO files")
        else:
            self.logger.warning("⚠️  DTO files not found")
    
    def _update_service_files(self, service_info: Dict, operations: List[FieldOperation], file_updater) -> None:
        """Update service files."""
        self.logger.info("⚙️  Updating service files...")
        
        entity_name = service_info.get('entity', service_info['name'].capitalize())
        service_path = self.project_root / "src" / "main" / "java" / "com" / "vira" / service_info['name'] / "service" / f"{entity_name}Service.java"
        
        if service_path.exists():
            success = file_updater.update_service_file(service_path, operations, service_info)
            if success:
                self.logger.info("✅ Service file updated successfully")
            else:
                self.logger.warning("⚠️  Failed to update service file")
        else:
            self.logger.warning(f"⚠️  Service file not found: {service_path}")
    
    def _update_repository_files(self, service_info: Dict, operations: List[FieldOperation]) -> None:
        """Update repository files."""
        self.logger.info("🗃️  Updating repository files...")
        
        # Repository interfaces typically don't need updates for simple field additions
        # Custom queries might need updates for new fields
        
        entity_name = service_info.get('entity', service_info['name'].capitalize())
        repo_path = self.project_root / "src" / "main" / "java" / "com" / "vira" / service_info['name'] / "repository" / f"{entity_name}Repository.java"
        
        if repo_path.exists():
            # Add custom query methods for new searchable fields
            try:
                with open(repo_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add finder methods for new string fields
                new_methods = []
                for operation in operations:
                    if operation.action == "add":
                        field_data = operation.field_data["field"]
                        if (field_data["javaType"] == "String" and 
                            field_data.get("validation", {}).get("maxLength", 0) <= 255):
                            
                            field_name = field_data["name"]
                            pascal_case = self._to_pascal_case(field_name)
                            
                            method = f"""
    /**
     * Find {entity_name.lower()}s by {field_name.replace('_', ' ')}.
     * 
     * @param {self._to_camel_case(field_name)} the {field_name.replace('_', ' ')}
     * @return list of {entity_name.lower()}s
     */
    List<{entity_name}> findBy{pascal_case}(String {self._to_camel_case(field_name)});
    
    /**
     * Find {entity_name.lower()}s by {field_name.replace('_', ' ')} containing text (case-insensitive).
     * 
     * @param {self._to_camel_case(field_name)} the {field_name.replace('_', ' ')} to search for
     * @return list of {entity_name.lower()}s
     */
    List<{entity_name}> findBy{pascal_case}ContainingIgnoreCase(String {self._to_camel_case(field_name)});
"""
                            new_methods.append(method)
                
                if new_methods:
                    # Insert before the closing brace
                    insert_pos = content.rfind('}')
                    if insert_pos > 0:
                        updated_content = content[:insert_pos] + '\n'.join(new_methods) + '\n' + content[insert_pos:]
                        
                        with open(repo_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        self.logger.info("✅ Repository file updated with new query methods")
                    else:
                        self.logger.warning("⚠️  Could not find insertion point in repository file")
                else:
                    self.logger.info("ℹ️  No repository updates needed")
                    
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to update repository file: {str(e)}")
        else:
            self.logger.warning(f"⚠️  Repository file not found: {repo_path}")
    
    def _update_controller_files(self, service_info: Dict, operations: List[FieldOperation]) -> None:
        """Update controller files."""
        self.logger.info("🌐 Updating controller files...")
        
        # Controllers typically don't need updates for field changes
        # The DTO changes handle the API contract updates
        
        self.logger.info("ℹ️  Controller files use DTOs, no direct updates needed")
    
    def _update_test_files(self, service_info: Dict, operations: List[FieldOperation]) -> None:
        """Update test files."""
        self.logger.info("🧪 Updating test files...")
        
        # Update test data and validation tests
        entity_name = service_info.get('entity', service_info['name'].capitalize())
        test_dir = self.project_root / "src" / "test" / "java" / "com" / "vira" / service_info['name']
        
        # Update service test
        service_test_path = test_dir / "service" / f"{entity_name}ServiceTest.java"
        if service_test_path.exists():
            try:
                with open(service_test_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add test data for new fields
                test_updates = []
                for operation in operations:
                    if operation.action == "add":
                        field_data = operation.field_data["field"]
                        if not field_data.get("autoGenerated", False):
                            test_value = self._get_test_value(field_data)
                            camel_case = self._to_camel_case(field_data["name"])
                            pascal_case = self._to_pascal_case(field_data["name"])
                            
                            test_updates.append(f"        .{camel_case}({test_value})")
                
                if test_updates:
                    # This is a simplified update - in a full implementation,
                    # you'd parse the test methods and update them properly
                    self.logger.info("ℹ️  Test file updates identified (manual review recommended)")
                else:
                    self.logger.info("ℹ️  No test file updates needed")
                    
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to update test file: {str(e)}")
        else:
            self.logger.warning(f"⚠️  Test file not found: {service_test_path}")
    
    def _update_react_files(self, service_info: Dict, operations: List[FieldOperation]) -> None:
        """Update React API service files."""
        self.logger.info("⚛️  Updating React files...")
        
        frontend_dir = self.project_root / "src" / "main" / "resources" / "frontend"
        if not frontend_dir.exists():
            frontend_dir.mkdir(parents=True, exist_ok=True)
        
        entity_name = service_info.get('entity', service_info['name'].capitalize())
        api_service_path = frontend_dir / "api" / f"{entity_name.lower()}ApiService.js"
        
        # Generate updated React API service
        try:
            # Create simple TypeScript interface updates
            interface_updates = []
            
            for operation in operations:
                if operation.action == "add":
                    field_data = operation.field_data["field"]
                    if not field_data.get("autoGenerated", False):
                        camel_case = self._to_camel_case(field_data["name"])
                        ts_type = self._java_to_typescript_type(field_data["javaType"])
                        required = "" if field_data.get("nullable", True) else ""
                        
                        interface_updates.append(f"  {camel_case}{required}: {ts_type};  // {field_data.get('description', '')}")
                elif operation.action == "remove":
                    field_name = operation.field_data["field_name"]
                    camel_case = self._to_camel_case(field_name)
                    interface_updates.append(f"  // REMOVED: {camel_case}")
            
            if interface_updates:
                # Create a simple update file for manual integration
                update_file_path = frontend_dir / f"{entity_name}_interface_updates.txt"
                with open(update_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"// Interface updates for {entity_name}\n")
                    f.write(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("// Add these fields to your TypeScript interfaces:\n\n")
                    for update in interface_updates:
                        f.write(update + "\n")
                
                self.logger.info(f"✅ React interface updates generated: {update_file_path.name}")
            else:
                self.logger.info("ℹ️  No React file updates needed")
                
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to update React files: {str(e)}")
    
    def _get_test_value(self, field_data: Dict) -> str:
        """Get a test value for a field."""
        java_type = field_data["javaType"]
        
        if java_type == "String":
            return f'"test_{field_data["name"]}"'
        elif java_type == "Boolean":
            return "true"
        elif java_type in ["Integer", "Long"]:
            return "1"
        elif java_type == "BigDecimal":
            return "new BigDecimal(\"100.00\")"
        elif java_type == "LocalDateTime":
            return "LocalDateTime.now()"
        elif java_type == "LocalDate":
            return "LocalDate.now()"
        else:
            return "null"
    
    def _java_to_typescript_type(self, java_type: str) -> str:
        """Convert Java type to TypeScript type."""
        mapping = {
            "String": "string",
            "Boolean": "boolean",
            "Integer": "number",
            "Long": "number",
            "BigDecimal": "number",
            "LocalDateTime": "string",
            "LocalDate": "string"
        }
        return mapping.get(java_type, "any")
    
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


@click.command()
@click.option('--config', '-c', default='config.json', help='Configuration file path')
@click.option('--operations', '-o', required=True, help='Field operations JSON file')
@click.option('--dry-run', is_flag=True, help='Show what would be changed without applying')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(config: str, operations: str, dry_run: bool, verbose: bool):
    """
    Vira Services Field Modifier
    
    Modify existing services by adding, updating, or removing fields.
    """
    try:
        # Create field modifier
        modifier = FieldModifier(config)
        
        # Set verbose logging if requested
        if verbose:
            modifier.logger.setLevel(logging.DEBUG)
        
        # Override dry-run if specified
        if dry_run:
            with open(operations, 'r') as f:
                ops_data = json.load(f)
            ops_data.setdefault('options', {})['dry_run'] = True
            
            temp_file = operations + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(ops_data, f, indent=2)
            
            operations = temp_file
        
        # Process field operations
        success = modifier.process_field_operations(operations)
        
        # Clean up temp file
        if dry_run and operations.endswith('.tmp'):
            Path(operations).unlink()
        
        if success:
            print("\n🎉 Field modification completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Field modification failed. Check logs for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 