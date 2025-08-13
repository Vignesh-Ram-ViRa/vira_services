# 🚀 Vira Services Code Generator - Installation Guide

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Installation](#quick-installation)
- [Manual Installation](#manual-installation)
- [Configuration Setup](#configuration-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Advanced Setup](#advanced-setup)

## 🔧 Prerequisites

### **System Requirements**
- **Python 3.8+** (Python 3.9 or higher recommended)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 512MB RAM for the generator
- **Disk Space**: ~50MB for the utility and dependencies

### **Check Your Python Version**
```bash
python --version
# or
python3 --version

# Should show Python 3.8.0 or higher
```

### **Install pip (if not already installed)**
```bash
# On Windows
python -m ensurepip --upgrade

# On macOS/Linux
python3 -m ensurepip --upgrade
```

## ⚡ Quick Installation

### **1. Download the Utilities**
```bash
# If you have the vira_services project
cd your_project_directory/vira_services

# The utilities folder should be present
ls utilities/
```

### **2. Install Dependencies**
```bash
cd utilities
pip install -r requirements.txt
```

### **3. Setup Configuration**
```bash
# Copy the sample config and customize it
cp config.json my_config.json

# Edit the paths in my_config.json to match your project
# Update the "paths" section with your actual project paths
```

### **4. Test Installation**
```bash
# Run the test suite
python test_field_management.py

# Should show all tests passing
```

### **5. Generate Your First Service**
```bash
# Create a new service
python generator.py --definition examples/blog_service.json

# Or add fields to existing service
python generator.py --definition examples/field_modifications/add_fields_finance.json --dry-run
```

## 📦 Manual Installation

### **Step 1: Create Project Directory**
```bash
# Create utilities directory if it doesn't exist
mkdir utilities
cd utilities
```

### **Step 2: Download Required Files**
Download these files to your `utilities` directory:
- `generator.py` - Main generator script
- `field_modifier.py` - Field management functionality
- `file_updater.py` - Java file updating utilities
- `config.json` - Configuration template
- `service_definition.json` - Service template
- `requirements.txt` - Python dependencies
- `README.md` - Documentation

### **Step 3: Install Python Dependencies**

#### **Option A: Using requirements.txt**
```bash
pip install -r requirements.txt
```

#### **Option B: Manual Installation**
```bash
pip install Jinja2==3.1.3
pip install jsonschema==4.21.1
pip install colorlog==6.8.2
pip install pathlib2==2.3.7.post1
pip install python-dateutil==2.9.0
pip install PyYAML==6.0.1
pip install regex==2023.12.25
pip install click==8.1.7
pip install tqdm==4.66.2
```

### **Step 4: Create Templates Directory**
```bash
# Create template directories
mkdir -p templates/field_operations
mkdir -p templates
mkdir -p examples/field_modifications
mkdir -p logs
mkdir -p backups
```

### **Step 5: Download Templates**
Ensure you have these template files:
- `templates/model.java.j2`
- `templates/repository.java.j2`
- `templates/service.java.j2`
- `templates/controller.java.j2`
- `templates/request_dto.java.j2`
- `templates/response_dto.java.j2`
- `templates/migration.sql.j2`
- `templates/react_api_service.js.j2`
- `templates/field_operations/migration_alter.sql.j2`

## ⚙️ Configuration Setup

### **1. Basic Configuration**

Edit `config.json` to match your project structure:

```json
{
  "paths": {
    "vira_services_root": "/path/to/your/vira_services",
    "src_main_java": "/path/to/your/vira_services/src/main/java/com/vira",
    "src_main_resources": "/path/to/your/vira_services/src/main/resources",
    "migration_path": "/path/to/your/vira_services/src/main/resources/db/migration",
    "frontend_resources": "/path/to/your/vira_services/src/main/resources/frontend"
  }
}
```

### **2. Windows Path Configuration**
```json
{
  "paths": {
    "vira_services_root": "C:/Users/YourName/Desktop/vira_services",
    "src_main_java": "C:/Users/YourName/Desktop/vira_services/src/main/java/com/vira",
    "src_main_resources": "C:/Users/YourName/Desktop/vira_services/src/main/resources",
    "migration_path": "C:/Users/YourName/Desktop/vira_services/src/main/resources/db/migration",
    "frontend_resources": "C:/Users/YourName/Desktop/vira_services/src/main/resources/frontend"
  }
}
```

### **3. macOS/Linux Path Configuration**
```json
{
  "paths": {
    "vira_services_root": "/Users/yourname/projects/vira_services",
    "src_main_java": "/Users/yourname/projects/vira_services/src/main/java/com/vira",
    "src_main_resources": "/Users/yourname/projects/vira_services/src/main/resources",
    "migration_path": "/Users/yourname/projects/vira_services/src/main/resources/db/migration",
    "frontend_resources": "/Users/yourname/projects/vira_services/src/main/resources/frontend"
  }
}
```

### **4. Verify Paths**
```bash
# Test if paths are correct
python -c "
import json
with open('config.json') as f:
    config = json.load(f)
    
import os
for name, path in config['paths'].items():
    exists = os.path.exists(path) if name != 'frontend_resources' else True
    print(f'{name}: {path} - {'✅ EXISTS' if exists else '❌ NOT FOUND'}')
"
```

## ✅ Verification

### **1. Run Test Suite**
```bash
python test_field_management.py
```

Expected output:
```
🚀 Starting Comprehensive Field Management Test
============================================================
Json Validation          ✅ PASS
Backup Functionality     ✅ PASS
Dry Run Mode             ✅ PASS
Impact Analysis          ✅ PASS
File Parser              ✅ PASS
Template Rendering       ✅ PASS
============================================================
Overall: 6/6 tests passed (100.0%)
🎉 ALL TESTS PASSED! Field management is ready for use.
```

### **2. Test Service Generation**
```bash
# Test creating a new service (dry run)
python generator.py --definition examples/blog_service.json --dry-run

# Should show generated files without creating them
```

### **3. Test Field Management**
```bash
# Test field operations (dry run)
python generator.py --definition examples/field_modifications/add_fields_finance.json --dry-run

# Should show impact analysis and preview changes
```

### **4. Check Utility Help**
```bash
python generator.py --help

# Should show all available options
```

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'jinja2'
pip install -r requirements.txt

# or install individual packages
pip install Jinja2 jsonschema colorlog
```

#### **2. Path Issues**
```bash
# Error: Path not found
# Solution: Update config.json with correct absolute paths

# Get current directory
pwd

# Update paths in config.json to absolute paths
```

#### **3. Permission Errors**
```bash
# On Windows: Run as Administrator if needed
# On macOS/Linux: Check file permissions

chmod +x generator.py
chmod +x test_field_management.py
```

#### **4. Python Version Issues**
```bash
# If default python is 2.x, use python3
python3 generator.py --help

# Or create an alias
alias python=python3
```

#### **5. Template Not Found**
```bash
# Error: Template not found
# Solution: Ensure templates directory exists and has .j2 files

ls templates/
ls templates/field_operations/

# Download missing templates if needed
```

### **Debugging**

#### **Enable Verbose Logging**
```bash
python generator.py --definition your_definition.json --verbose

# Shows detailed logs of what's happening
```

#### **Check Logs**
```bash
# Check log files
cat logs/generator.log

# Or view recent logs
tail -n 50 logs/generator.log
```

#### **Validate JSON**
```bash
# Test JSON syntax
python -m json.tool your_definition.json

# Should pretty-print if valid, show error if invalid
```

## 🚀 Advanced Setup

### **1. Create Executable (Optional)**

Create a standalone .exe file (Windows):

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --name vira-generator generator.py

# Executable will be in dist/vira-generator.exe
```

### **2. Environment Variables**

Set up environment variables for paths:

#### **Windows**
```batch
set VIRA_ROOT=C:\path\to\vira_services
set VIRA_CONFIG=C:\path\to\utilities\config.json

python generator.py --config %VIRA_CONFIG%
```

#### **macOS/Linux**
```bash
export VIRA_ROOT="/path/to/vira_services"
export VIRA_CONFIG="/path/to/utilities/config.json"

python generator.py --config $VIRA_CONFIG
```

### **3. IDE Integration**

#### **VSCode**
Add to your `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate Service",
      "type": "shell",
      "command": "python",
      "args": ["utilities/generator.py", "--definition", "${input:definitionFile}"],
      "group": "build",
      "presentation": {
        "panel": "new"
      }
    }
  ],
  "inputs": [
    {
      "id": "definitionFile",
      "type": "promptString",
      "description": "Path to service definition JSON file"
    }
  ]
}
```

### **4. Batch Processing**

Create batch scripts for common operations:

#### **Windows (generate_service.bat)**
```batch
@echo off
cd utilities
python generator.py --definition %1 %2 %3
pause
```

#### **macOS/Linux (generate_service.sh)**
```bash
#!/bin/bash
cd utilities
python generator.py --definition "$1" "$2" "$3"
```

## 🎉 You're Ready!

Your Vira Services Code Generator is now installed and ready to use!

### **Next Steps:**
1. 📚 Read the [README.md](README.md) for usage examples
2. 🔧 Try the [examples](examples/) directory
3. 📋 Review the [Field Management Guide](FIELD_MANAGEMENT_PLAN.md)
4. 🚀 Start generating your services!

### **Quick Commands:**
```bash
# Generate new service
python generator.py --definition service_definition.json

# Add fields to existing service
python generator.py --definition field_operations.json

# Preview changes (dry run)
python generator.py --definition definition.json --dry-run

# Run tests
python test_field_management.py
```

**Happy coding! 🎯** 