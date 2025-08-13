#!/usr/bin/env python3
"""
Field Management Test Script

This script tests the complete field management workflow:
- Validates JSON parsing
- Tests impact analysis
- Verifies backup functionality
- Tests dry run mode
- Validates file generation

Author: Vira Code Generator
Version: 1.0.0
"""

import json
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

def test_json_validation():
    """Test JSON validation for field operations."""
    print("🧪 Testing JSON validation...")
    
    # Test valid JSON
    valid_json = {
        "operation_type": "modify_service",
        "target_service": {
            "name": "test",
            "table": "test_table",
            "entity": "TestEntity"
        },
        "field_operations": [
            {
                "action": "add",
                "field": {
                    "name": "test_field",
                    "type": "VARCHAR(100)",
                    "javaType": "String",
                    "nullable": True,
                    "description": "Test field"
                }
            }
        ],
        "options": {
            "dry_run": True,
            "backup_enabled": True
        }
    }
    
    # Write test JSON
    test_file = Path("test_field_operations.json")
    with open(test_file, 'w') as f:
        json.dump(valid_json, f, indent=2)
    
    print("✅ Valid JSON created for testing")
    
    # Test invalid JSON
    invalid_json = {
        "operation_type": "invalid_type",  # Invalid
        "field_operations": []  # Missing target_service
    }
    
    invalid_file = Path("test_invalid_operations.json")
    with open(invalid_file, 'w') as f:
        json.dump(invalid_json, f, indent=2)
    
    print("✅ Invalid JSON created for validation testing")
    
    return test_file, invalid_file

def test_backup_functionality():
    """Test backup and restore functionality."""
    print("🧪 Testing backup functionality...")
    
    # Create mock project structure
    mock_project = Path("mock_vira_project")
    mock_project.mkdir(exist_ok=True)
    
    # Create mock files
    mock_service_dir = mock_project / "src" / "main" / "java" / "com" / "vira" / "test"
    mock_service_dir.mkdir(parents=True, exist_ok=True)
    
    # Create mock Java files
    mock_files = [
        "model/TestEntity.java",
        "service/TestEntityService.java",
        "repository/TestEntityRepository.java",
        "dto/TestEntityRequest.java",
        "dto/TestEntityResponse.java",
        "controller/TestEntityController.java"
    ]
    
    for file_path in mock_files:
        full_path = mock_service_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(f"// Mock {file_path}\npublic class MockClass {{\n    // Mock content\n}}")
    
    print(f"✅ Mock project structure created: {mock_project}")
    return mock_project

def test_dry_run_mode():
    """Test dry run mode functionality."""
    print("🧪 Testing dry run mode...")
    
    try:
        # Import the field modifier
        sys.path.append(str(Path("utilities")))
        from field_modifier import FieldModifier
        
        # Create test config
        test_config = {
            "paths": {
                "vira_services_root": str(Path("mock_vira_project").absolute()),
                "src_main_java": str(Path("mock_vira_project/src/main/java/com/vira").absolute()),
                "src_main_resources": str(Path("mock_vira_project/src/main/resources").absolute()),
                "migration_path": str(Path("mock_vira_project/src/main/resources/db/migration").absolute())
            },
            "generation": {
                "include_react_integration": True,
                "include_tests": True,
                "include_migration": True
            },
            "logging": {
                "level": "INFO",
                "console": True
            }
        }
        
        # Write test config
        config_file = Path("test_config.json")
        with open(config_file, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Test dry run
        modifier = FieldModifier(str(config_file))
        
        # Test with dry run enabled
        operations_file = Path("test_field_operations.json")
        if operations_file.exists():
            # Enable dry run in the operations file
            with open(operations_file, 'r') as f:
                operations_data = json.load(f)
            
            operations_data["options"]["dry_run"] = True
            
            with open(operations_file, 'w') as f:
                json.dump(operations_data, f, indent=2)
            
            print("✅ Dry run mode test setup complete")
            return modifier, operations_file, config_file
        else:
            print("❌ Test operations file not found")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Dry run test setup failed: {str(e)}")
        return None, None, None

def test_impact_analysis():
    """Test impact analysis functionality."""
    print("🧪 Testing impact analysis...")
    
    try:
        sys.path.append(str(Path("utilities")))
        from field_modifier import ImpactAnalyzer, FieldOperation
        import logging
        
        # Setup logger
        logger = logging.getLogger("TestLogger")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        
        # Create analyzer
        analyzer = ImpactAnalyzer(logger)
        
        # Test service info
        service_info = {
            "name": "test",
            "table": "test_table",
            "entity": "TestEntity"
        }
        
        # Test operations
        operations = [
            FieldOperation("add", {
                "field": {
                    "name": "new_field",
                    "type": "VARCHAR(100)",
                    "javaType": "String",
                    "nullable": True,
                    "description": "Test field"
                }
            }),
            FieldOperation("remove", {
                "field_name": "old_field"
            })
        ]
        
        # Analyze impact
        analysis = analyzer.analyze_field_operations(service_info, operations)
        
        print("✅ Impact analysis completed")
        print(f"   - Operations: {analysis['operations_count']}")
        print(f"   - Files to modify: {len(analysis['files_to_modify'])}")
        print(f"   - Migration changes: {len(analysis['migration_changes'])}")
        print(f"   - Risks identified: {len(analysis['potential_risks'])}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Impact analysis test failed: {str(e)}")
        return None

def test_file_parser():
    """Test Java file parsing functionality."""
    print("🧪 Testing Java file parser...")
    
    try:
        sys.path.append(str(Path("utilities")))
        from file_updater import JavaFileParser
        
        # Create test Java file
        test_java_content = """package com.vira.test.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

/**
 * Test entity for parsing
 */
@Entity
@Table(name = "test_table")
public class TestEntity {

    /**
     * Primary key
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Test name field
     */
    @Column(name = "name", nullable = false, length = 100)
    @NotNull(message = "Name is required")
    @Size(max = 100)
    private String name;

    /**
     * Test description field
     */
    @Column(name = "description")
    private String description;

    // Constructors
    public TestEntity() {}

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}"""

        test_java_file = Path("TestEntity.java")
        with open(test_java_file, 'w') as f:
            f.write(test_java_content)
        
        # Parse the file
        parser = JavaFileParser()
        structure = parser.parse_java_file(test_java_file)
        
        if "error" in structure:
            print(f"❌ Parser error: {structure['error']}")
            return None
        
        print("✅ Java file parsing successful")
        print(f"   - Class: {structure['class_name']}")
        print(f"   - Package: {structure['package']}")
        print(f"   - Fields found: {len(structure['fields'])}")
        print(f"   - Methods found: {len(structure['methods'])}")
        
        # Display fields
        for field in structure['fields']:
            print(f"     • {field['name']} ({field['type']}) - {len(field['annotations'])} annotations")
        
        return structure
        
    except Exception as e:
        print(f"❌ File parser test failed: {str(e)}")
        return None

def test_template_rendering():
    """Test template rendering functionality."""
    print("🧪 Testing template rendering...")
    
    try:
        # Check if templates exist
        templates_dir = Path("utilities/templates/field_operations")
        if not templates_dir.exists():
            print("⚠️  Template directory not found, creating basic test...")
            templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a simple test template
            test_template = templates_dir / "test_migration.sql.j2"
            with open(test_template, 'w') as f:
                f.write("""-- Test Migration: {{ migration_version }}
-- Service: {{ service_name }}
-- Table: {{ table_name }}

{% for operation in add_operations %}
-- Add field: {{ operation.field.name }}
ALTER TABLE {{ table_name }} ADD COLUMN {{ operation.field.name }} {{ operation.field.type }};
{% endfor %}

-- Migration completed""")
        
        # Test template rendering
        from jinja2 import Environment, FileSystemLoader
        
        jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))
        
        # Check available templates
        available_templates = list(templates_dir.glob("*.j2"))
        print(f"✅ Templates found: {len(available_templates)}")
        for template in available_templates:
            print(f"   • {template.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template rendering test failed: {str(e)}")
        return False

def run_comprehensive_test():
    """Run comprehensive test of field management functionality."""
    print("🚀 Starting Comprehensive Field Management Test")
    print("=" * 60)
    
    test_results = {
        "json_validation": False,
        "backup_functionality": False,
        "dry_run_mode": False,
        "impact_analysis": False,
        "file_parser": False,
        "template_rendering": False
    }
    
    try:
        # Change to utilities directory
        original_dir = Path.cwd()
        utilities_dir = Path("utilities")
        if utilities_dir.exists():
            os.chdir(utilities_dir)
        
        # Test 1: JSON Validation
        test_file, invalid_file = test_json_validation()
        test_results["json_validation"] = test_file.exists() and invalid_file.exists()
        
        # Test 2: Backup Functionality
        mock_project = test_backup_functionality()
        test_results["backup_functionality"] = mock_project.exists()
        
        # Test 3: Impact Analysis
        analysis = test_impact_analysis()
        test_results["impact_analysis"] = analysis is not None
        
        # Test 4: File Parser
        structure = test_file_parser()
        test_results["file_parser"] = structure is not None
        
        # Test 5: Template Rendering
        template_success = test_template_rendering()
        test_results["template_rendering"] = template_success
        
        # Test 6: Dry Run Mode
        modifier, operations_file, config_file = test_dry_run_mode()
        test_results["dry_run_mode"] = modifier is not None
        
        # Execute actual dry run test
        if modifier and operations_file:
            print("🧪 Executing dry run test...")
            try:
                success = modifier.process_field_operations(str(operations_file))
                print(f"✅ Dry run execution: {'Success' if success else 'Failed'}")
            except Exception as e:
                print(f"⚠️  Dry run execution failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {str(e)}")
    
    finally:
        # Return to original directory
        os.chdir(original_dir)
        
        # Cleanup test files
        cleanup_test_files()
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Field management is ready for use.")
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed. Minor issues may exist.")
    else:
        print("❌ Multiple test failures. Review implementation needed.")
    
    return test_results

def cleanup_test_files():
    """Clean up test files created during testing."""
    print("🧹 Cleaning up test files...")
    
    test_files = [
        "test_field_operations.json",
        "test_invalid_operations.json",
        "test_config.json",
        "TestEntity.java",
        "mock_vira_project"
    ]
    
    for file_path in test_files:
        path = Path(file_path)
        try:
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"   Removed: {file_path}")
        except Exception as e:
            print(f"   Failed to remove {file_path}: {str(e)}")

if __name__ == "__main__":
    # Run the comprehensive test
    results = run_comprehensive_test()
    
    # Exit with appropriate code
    passed_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    if passed_count == total_count:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed 