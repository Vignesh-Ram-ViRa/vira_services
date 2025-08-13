#!/usr/bin/env python3
"""
File Updater for Vira Services Field Operations

This module handles updating existing Java files when fields are modified:
- Model classes (JPA entities)
- DTO classes (Request/Response)
- Service classes
- Repository interfaces
- Controller classes
- Test classes

Author: Vira Code Generator
Version: 1.0.0
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError as e:
    print(f"ERROR: Missing required dependency: {e}")
    exit(1)


class JavaFileParser:
    """Parses Java files to understand their structure."""
    
    def __init__(self):
        self.class_pattern = re.compile(r'public\s+class\s+(\w+)')
        self.field_pattern = re.compile(r'private\s+(\w+(?:<.*?>)?)\s+(\w+);')
        self.method_pattern = re.compile(r'public\s+(\w+(?:<.*?>)?)\s+(\w+)\s*\([^)]*\)')
        self.annotation_pattern = re.compile(r'@(\w+)(?:\([^)]*\))?')
    
    def parse_java_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Java file and extract its structure.
        
        Args:
            file_path: Path to the Java file
            
        Returns:
            Dictionary containing file structure
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            structure = {
                "file_path": str(file_path),
                "content": content,
                "lines": content.split('\n'),
                "package": self._extract_package(content),
                "imports": self._extract_imports(content),
                "class_name": self._extract_class_name(content),
                "fields": self._extract_fields(content),
                "methods": self._extract_methods(content),
                "annotations": self._extract_class_annotations(content)
            }
            
            return structure
            
        except Exception as e:
            return {"error": f"Failed to parse file: {str(e)}"}
    
    def _extract_package(self, content: str) -> Optional[str]:
        """Extract package declaration."""
        match = re.search(r'package\s+([\w.]+);', content)
        return match.group(1) if match else None
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements."""
        imports = re.findall(r'import\s+([\w.*]+);', content)
        return imports
    
    def _extract_class_name(self, content: str) -> Optional[str]:
        """Extract class name."""
        match = self.class_pattern.search(content)
        return match.group(1) if match else None
    
    def _extract_fields(self, content: str) -> List[Dict[str, Any]]:
        """Extract field declarations with their annotations."""
        fields = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            field_match = self.field_pattern.search(line.strip())
            if field_match:
                field_type = field_match.group(1)
                field_name = field_match.group(2)
                
                # Look backwards for annotations
                annotations = []
                j = i - 1
                while j >= 0 and (lines[j].strip().startswith('@') or lines[j].strip() == ''):
                    if lines[j].strip().startswith('@'):
                        annotations.insert(0, lines[j].strip())
                    j -= 1
                
                # Look backwards for JavaDoc
                javadoc = []
                while j >= 0 and (lines[j].strip().startswith('*') or lines[j].strip().startswith('/**') or lines[j].strip() == ''):
                    if lines[j].strip():
                        javadoc.insert(0, lines[j].strip())
                    j -= 1
                
                fields.append({
                    "name": field_name,
                    "type": field_type,
                    "annotations": annotations,
                    "javadoc": javadoc,
                    "line_number": i
                })
        
        return fields
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method declarations."""
        methods = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            method_match = self.method_pattern.search(line.strip())
            if method_match and not line.strip().startswith('//'):
                return_type = method_match.group(1)
                method_name = method_match.group(2)
                
                methods.append({
                    "name": method_name,
                    "return_type": return_type,
                    "line_number": i,
                    "full_line": line.strip()
                })
        
        return methods
    
    def _extract_class_annotations(self, content: str) -> List[str]:
        """Extract class-level annotations."""
        lines = content.split('\n')
        annotations = []
        
        for line in lines:
            if line.strip().startswith('@') and 'public class' not in line:
                annotations.append(line.strip())
            elif 'public class' in line:
                break
        
        return annotations


class JavaFileUpdater:
    """Updates Java files by adding, modifying, or removing fields."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.parser = JavaFileParser()
        self.template_env = None
    
    def setup_templates(self):
        """Setup Jinja2 templates for code generation."""
        templates_dir = Path("templates")
        if templates_dir.exists():
            self.template_env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
    
    def update_model_file(self, file_path: Path, field_operations: List[Any], service_info: Dict) -> bool:
        """
        Update a JPA model file with field operations.
        
        Args:
            file_path: Path to the model file
            field_operations: List of field operations to apply
            service_info: Information about the service
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Updating model file: {file_path}")
            
            # Parse existing file
            structure = self.parser.parse_java_file(file_path)
            if "error" in structure:
                self.logger.error(f"Failed to parse model file: {structure['error']}")
                return False
            
            # Apply field operations
            updated_content = self._apply_model_operations(structure, field_operations, service_info)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.logger.info(f"✅ Model file updated successfully: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update model file: {str(e)}")
            return False
    
    def update_dto_files(self, request_path: Path, response_path: Path, field_operations: List[Any], service_info: Dict) -> bool:
        """
        Update DTO files (Request and Response) with field operations.
        
        Args:
            request_path: Path to the request DTO file
            response_path: Path to the response DTO file
            field_operations: List of field operations to apply
            service_info: Information about the service
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Updating DTO files: {request_path}, {response_path}")
            
            # Update Request DTO
            if request_path.exists():
                request_structure = self.parser.parse_java_file(request_path)
                if "error" not in request_structure:
                    updated_request = self._apply_dto_operations(request_structure, field_operations, service_info, "request")
                    with open(request_path, 'w', encoding='utf-8') as f:
                        f.write(updated_request)
            
            # Update Response DTO
            if response_path.exists():
                response_structure = self.parser.parse_java_file(response_path)
                if "error" not in response_structure:
                    updated_response = self._apply_dto_operations(response_structure, field_operations, service_info, "response")
                    with open(response_path, 'w', encoding='utf-8') as f:
                        f.write(updated_response)
            
            self.logger.info("✅ DTO files updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update DTO files: {str(e)}")
            return False
    
    def update_service_file(self, file_path: Path, field_operations: List[Any], service_info: Dict) -> bool:
        """
        Update service file with field operations.
        
        Args:
            file_path: Path to the service file
            field_operations: List of field operations to apply
            service_info: Information about the service
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Updating service file: {file_path}")
            
            # Parse existing file
            structure = self.parser.parse_java_file(file_path)
            if "error" in structure:
                self.logger.error(f"Failed to parse service file: {structure['error']}")
                return False
            
            # Apply field operations (mainly update validation and mapping methods)
            updated_content = self._apply_service_operations(structure, field_operations, service_info)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.logger.info(f"✅ Service file updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update service file: {str(e)}")
            return False
    
    def _apply_model_operations(self, structure: Dict, operations: List[Any], service_info: Dict) -> str:
        """Apply field operations to model file content."""
        lines = structure["lines"][:]
        existing_fields = {field["name"]: field for field in structure["fields"]}
        
        # Find the class declaration to insert new fields after existing ones
        class_start = -1
        last_field_line = -1
        
        for i, line in enumerate(lines):
            if "public class" in line and service_info.get("entity", "") in line:
                class_start = i
            
            # Find the last field declaration
            for field in structure["fields"]:
                if field["line_number"] > last_field_line:
                    last_field_line = field["line_number"]
        
        # Apply operations in reverse order to maintain line numbers
        for operation in reversed(operations):
            if operation.action == "add":
                field_data = operation.field_data["field"]
                field_code = self._generate_model_field_code(field_data)
                
                # Insert after last field or after class declaration
                insert_line = last_field_line + 1 if last_field_line > -1 else class_start + 2
                
                # Insert field code
                field_lines = field_code.split('\n')
                for j, field_line in enumerate(field_lines):
                    lines.insert(insert_line + j, field_line)
                
                last_field_line += len(field_lines)
            
            elif operation.action == "remove":
                field_name = operation.field_data["field_name"]
                if field_name in existing_fields:
                    field_info = existing_fields[field_name]
                    
                    # Remove field and its annotations/javadoc
                    start_line = field_info["line_number"]
                    end_line = start_line
                    
                    # Find start of field block (including annotations)
                    while start_line > 0 and (lines[start_line-1].strip().startswith('@') or 
                                            lines[start_line-1].strip().startswith('*') or
                                            lines[start_line-1].strip().startswith('/**') or
                                            lines[start_line-1].strip() == ''):
                        start_line -= 1
                    
                    # Remove lines
                    for _ in range(end_line - start_line + 1):
                        if start_line < len(lines):
                            lines.pop(start_line)
            
            elif operation.action == "update":
                field_name = operation.field_data["field_name"]
                changes = operation.field_data["changes"]
                
                if field_name in existing_fields:
                    field_info = existing_fields[field_name]
                    field_line = field_info["line_number"]
                    
                    # Update field type if specified
                    if "type" in changes:
                        java_type = self._sql_to_java_type(changes["type"])
                        pattern = rf'private\s+\w+(?:<.*?>)?\s+{field_name};'
                        replacement = f'private {java_type} {field_name};'
                        lines[field_line] = re.sub(pattern, replacement, lines[field_line])
                    
                    # Update validation annotations
                    if "validation" in changes:
                        self._update_field_annotations(lines, field_info, changes["validation"])
        
        return '\n'.join(lines)
    
    def _apply_dto_operations(self, structure: Dict, operations: List[Any], service_info: Dict, dto_type: str) -> str:
        """Apply field operations to DTO file content."""
        lines = structure["lines"][:]
        existing_fields = {field["name"]: field for field in structure["fields"]}
        
        # Find insertion point
        last_field_line = -1
        for field in structure["fields"]:
            if field["line_number"] > last_field_line:
                last_field_line = field["line_number"]
        
        # Apply operations
        for operation in reversed(operations):
            if operation.action == "add":
                field_data = operation.field_data["field"]
                
                # Skip auto-generated fields for request DTOs
                if dto_type == "request" and field_data.get("autoGenerated", False):
                    continue
                
                field_code = self._generate_dto_field_code(field_data, dto_type)
                
                # Insert field
                insert_line = last_field_line + 1 if last_field_line > -1 else len(lines) - 5
                field_lines = field_code.split('\n')
                for j, field_line in enumerate(field_lines):
                    lines.insert(insert_line + j, field_line)
                
                last_field_line += len(field_lines)
            
            elif operation.action == "remove":
                field_name = operation.field_data["field_name"]
                if field_name in existing_fields:
                    field_info = existing_fields[field_name]
                    self._remove_field_block(lines, field_info)
            
            elif operation.action == "update":
                field_name = operation.field_data["field_name"]
                changes = operation.field_data["changes"]
                
                if field_name in existing_fields:
                    self._update_dto_field(lines, existing_fields[field_name], changes)
        
        # Update getters/setters and constructors
        self._update_dto_methods(lines, operations, service_info, dto_type)
        
        return '\n'.join(lines)
    
    def _apply_service_operations(self, structure: Dict, operations: List[Any], service_info: Dict) -> str:
        """Apply field operations to service file content."""
        lines = structure["lines"][:]
        
        # Update validation methods and field mappings
        for operation in operations:
            if operation.action == "add":
                field_data = operation.field_data["field"]
                
                # Add validation for new fields
                if field_data.get("validation", {}).get("required"):
                    self._add_field_validation(lines, field_data, service_info)
                
                # Add field mapping in conversion methods
                self._add_field_mapping(lines, field_data, service_info)
            
            elif operation.action == "remove":
                field_name = operation.field_data["field_name"]
                self._remove_field_references(lines, field_name)
            
            elif operation.action == "update":
                field_name = operation.field_data["field_name"]
                changes = operation.field_data["changes"]
                self._update_field_validation(lines, field_name, changes)
        
        return '\n'.join(lines)
    
    def _generate_model_field_code(self, field_data: Dict) -> str:
        """Generate Java code for a model field."""
        code_lines = []
        
        # Add JavaDoc comment
        code_lines.append("    /**")
        code_lines.append(f"     * {field_data.get('description', field_data['name'])}")
        code_lines.append("     */")
        
        # Add JPA annotations
        if field_data.get("primaryKey"):
            code_lines.append("    @Id")
            if field_data.get("autoGenerated"):
                code_lines.append("    @GeneratedValue(strategy = GenerationType.IDENTITY)")
        
        if field_data.get("name") == "created_at" and field_data.get("autoGenerated"):
            code_lines.append("    @CreationTimestamp")
        elif field_data.get("name") == "updated_at" and field_data.get("updateOnModify"):
            code_lines.append("    @UpdateTimestamp")
        
        # Column annotation
        column_parts = [f'name = "{field_data["name"]}"']
        if not field_data.get("nullable", True):
            column_parts.append("nullable = false")
        if field_data.get("validation", {}).get("maxLength"):
            column_parts.append(f"length = {field_data['validation']['maxLength']}")
        
        code_lines.append(f"    @Column({', '.join(column_parts)})")
        
        # Validation annotations
        validation = field_data.get("validation", {})
        if validation.get("required"):
            code_lines.append("    @NotNull(message = \"" + field_data["name"].replace("_", " ").title() + " is required\")")
        
        if field_data["javaType"] == "String" and validation.get("maxLength"):
            code_lines.append(f"    @Size(max = {validation['maxLength']}, message = \"" + 
                            field_data["name"].replace("_", " ").title() + 
                            f" cannot exceed {validation['maxLength']} characters\")")
        
        if field_data["javaType"] in ["BigDecimal", "Integer", "Long"] and validation.get("min") is not None:
            code_lines.append(f"    @DecimalMin(value = \"{validation['min']}\", message = \"" +
                            field_data["name"].replace("_", " ").title() + 
                            f" must be at least {validation['min']}\")")
        
        # Field declaration
        java_type = field_data["javaType"]
        camel_case_name = self._to_camel_case(field_data["name"])
        code_lines.append(f"    private {java_type} {camel_case_name};")
        code_lines.append("")
        
        return '\n'.join(code_lines)
    
    def _generate_dto_field_code(self, field_data: Dict, dto_type: str) -> str:
        """Generate Java code for a DTO field."""
        code_lines = []
        
        # Add JavaDoc comment
        code_lines.append("    /**")
        code_lines.append(f"     * {field_data.get('description', field_data['name'])}")
        code_lines.append("     */")
        
        # Add Swagger annotation
        example_value = self._get_example_value(field_data)
        required = "true" if field_data.get("validation", {}).get("required") and dto_type == "request" else "false"
        
        code_lines.append(f"    @Schema(description = \"{field_data.get('description', field_data['name'])}\",")
        code_lines.append(f"            required = {required},")
        if field_data.get("validation", {}).get("maxLength"):
            code_lines.append(f"            maxLength = {field_data['validation']['maxLength']},")
        code_lines.append(f"            example = \"{example_value}\")")
        
        # Add JSON property annotation
        code_lines.append(f"    @JsonProperty(\"{field_data['name']}\")")
        
        # Add validation annotations for request DTOs
        if dto_type == "request":
            validation = field_data.get("validation", {})
            if validation.get("required"):
                code_lines.append("    @NotNull(message = \"" + field_data["name"].replace("_", " ").title() + " is required\")")
                if field_data["javaType"] == "String":
                    code_lines.append("    @NotBlank(message = \"" + field_data["name"].replace("_", " ").title() + " cannot be blank\")")
            
            if field_data["javaType"] == "String" and validation.get("maxLength"):
                code_lines.append(f"    @Size(max = {validation['maxLength']}, message = \"" + 
                                field_data["name"].replace("_", " ").title() + 
                                f" cannot exceed {validation['maxLength']} characters\")")
        
        # Field declaration
        java_type = field_data["javaType"]
        camel_case_name = self._to_camel_case(field_data["name"])
        code_lines.append(f"    private {java_type} {camel_case_name};")
        code_lines.append("")
        
        return '\n'.join(code_lines)
    
    def _remove_field_block(self, lines: List[str], field_info: Dict) -> None:
        """Remove a field block including annotations and JavaDoc."""
        start_line = field_info["line_number"]
        
        # Find start of field block
        while start_line > 0 and (lines[start_line-1].strip().startswith('@') or 
                                lines[start_line-1].strip().startswith('*') or
                                lines[start_line-1].strip().startswith('/**') or
                                lines[start_line-1].strip() == ''):
            start_line -= 1
        
        # Remove lines
        end_line = field_info["line_number"]
        for _ in range(end_line - start_line + 1):
            if start_line < len(lines):
                lines.pop(start_line)
    
    def _update_field_annotations(self, lines: List[str], field_info: Dict, validation: Dict) -> None:
        """Update validation annotations for a field."""
        field_line = field_info["line_number"]
        
        # Remove old validation annotations
        i = field_line - 1
        while i >= 0 and lines[i].strip().startswith('@'):
            if any(anno in lines[i] for anno in ['@NotNull', '@Size', '@DecimalMin', '@DecimalMax']):
                lines.pop(i)
                field_line -= 1
            i -= 1
        
        # Add new validation annotations
        new_annotations = []
        if validation.get("required"):
            new_annotations.append("    @NotNull(message = \"Field is required\")")
        if validation.get("maxLength"):
            new_annotations.append(f"    @Size(max = {validation['maxLength']}, message = \"Field too long\")")
        
        for j, annotation in enumerate(new_annotations):
            lines.insert(field_line + j, annotation)
    
    def _update_dto_methods(self, lines: List[str], operations: List[Any], service_info: Dict, dto_type: str) -> None:
        """Update getter/setter methods and constructors in DTO."""
        # Find class end to insert new methods
        class_end = len(lines) - 2
        
        for operation in operations:
            if operation.action == "add":
                field_data = operation.field_data["field"]
                
                if dto_type == "request" and field_data.get("autoGenerated", False):
                    continue
                
                # Generate getter and setter
                camel_case_name = self._to_camel_case(field_data["name"])
                pascal_case_name = self._to_pascal_case(field_data["name"])
                java_type = field_data["javaType"]
                
                getter_setter = f"""
    /**
     * Get {field_data.get('description', field_data['name']).lower()}.
     * 
     * @return {field_data.get('description', field_data['name']).lower()}
     */
    public {java_type} get{pascal_case_name}() {{
        return {camel_case_name};
    }}

    /**
     * Set {field_data.get('description', field_data['name']).lower()}.
     * 
     * @param {camel_case_name} {field_data.get('description', field_data['name']).lower()}
     */
    public void set{pascal_case_name}({java_type} {camel_case_name}) {{
        this.{camel_case_name} = {camel_case_name};
    }}
"""
                # Insert before class closing brace
                getter_setter_lines = getter_setter.strip().split('\n')
                for j, line in enumerate(getter_setter_lines):
                    lines.insert(class_end + j, line)
                
                class_end += len(getter_setter_lines)
    
    def _add_field_validation(self, lines: List[str], field_data: Dict, service_info: Dict) -> None:
        """Add validation logic for new fields in service methods."""
        # Find validation method
        for i, line in enumerate(lines):
            if "validateCreateRequest" in line or "validateUpdateRequest" in line:
                # Find end of method
                j = i
                brace_count = 0
                while j < len(lines):
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                        if brace_count == 0:
                            break
                    j += 1
                
                # Insert validation before method end
                if field_data.get("validation", {}).get("required"):
                    camel_case_name = self._to_camel_case(field_data["name"])
                    field_title = field_data["name"].replace("_", " ").title()
                    
                    if field_data["javaType"] == "String":
                        validation_code = f"""        if (!StringUtils.hasText(request.get{self._to_pascal_case(field_data["name"])}())) {{
            throw new BusinessException("{field_title} is required");
        }}"""
                    else:
                        validation_code = f"""        if (request.get{self._to_pascal_case(field_data["name"])}() == null) {{
            throw new BusinessException("{field_title} is required");
        }}"""
                    
                    lines.insert(j - 1, validation_code)
                break
    
    def _add_field_mapping(self, lines: List[str], field_data: Dict, service_info: Dict) -> None:
        """Add field mapping in entity conversion methods."""
        camel_case_name = self._to_camel_case(field_data["name"])
        pascal_case_name = self._to_pascal_case(field_data["name"])
        
        # Find conversion methods and add field mapping
        for i, line in enumerate(lines):
            if "createEntityFromRequest" in line or "updateEntityFromRequest" in line or "convertToResponse" in line:
                # Find end of method
                j = i
                brace_count = 0
                while j < len(lines):
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                        if brace_count == 0:
                            break
                    j += 1
                
                # Add field mapping before method end
                if "createEntityFromRequest" in line and not field_data.get("autoGenerated", False):
                    mapping = f"        {service_info.get('entity', 'Entity').lower()}.set{pascal_case_name}(request.get{pascal_case_name}());"
                    lines.insert(j - 1, mapping)
                elif "convertToResponse" in line:
                    mapping = f"        response.set{pascal_case_name}({service_info.get('entity', 'Entity').lower()}.get{pascal_case_name}());"
                    lines.insert(j - 1, mapping)
    
    def _remove_field_references(self, lines: List[str], field_name: str) -> None:
        """Remove references to a field from service methods."""
        pascal_case_name = self._to_pascal_case(field_name)
        
        # Remove lines that reference the field
        i = 0
        while i < len(lines):
            if f"get{pascal_case_name}()" in lines[i] or f"set{pascal_case_name}(" in lines[i]:
                lines.pop(i)
            else:
                i += 1
    
    def _update_field_validation(self, lines: List[str], field_name: str, changes: Dict) -> None:
        """Update validation for an existing field."""
        pascal_case_name = self._to_pascal_case(field_name)
        
        # Find validation references and update them
        for i, line in enumerate(lines):
            if f"get{pascal_case_name}()" in line and "validation" in changes:
                # Update validation logic based on changes
                if "maxLength" in changes.get("validation", {}):
                    # Update length validation if present
                    pass  # Could add more sophisticated validation updates
    
    def _get_example_value(self, field_data: Dict) -> str:
        """Get example value for Swagger documentation."""
        java_type = field_data["javaType"]
        field_name = field_data["name"]
        
        if java_type == "String":
            return f"Sample {field_name.replace('_', ' ')}"
        elif java_type == "BigDecimal":
            return "100.50"
        elif java_type in ["Integer", "Long"]:
            return "1"
        elif java_type == "Boolean":
            return "true"
        elif java_type == "LocalDateTime":
            return "2024-01-15T10:30:00"
        elif java_type == "LocalDate":
            return "2024-01-15"
        else:
            return "sample"
    
    def _sql_to_java_type(self, sql_type: str) -> str:
        """Convert SQL type to Java type."""
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
        
        base_type = sql_type.split('(')[0].upper()
        return type_mapping.get(base_type, 'String')
    
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