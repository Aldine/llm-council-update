"""
Tree-shake and API Analysis Tool
Finds orphaned code and analyzes API response shapes
"""

import os
import json
import re
from pathlib import Path
from typing import Set, Dict, List
from collections import defaultdict

def find_python_files(directory: str) -> List[Path]:
    """Find all Python files in directory"""
    return list(Path(directory).rglob("*.py"))

def find_js_files(directory: str) -> List[Path]:
    """Find all JS/JSX files in directory"""
    jsx_files = list(Path(directory).rglob("*.jsx"))
    js_files = list(Path(directory).rglob("*.js"))
    return jsx_files + js_files

def extract_functions(filepath: Path) -> Set[str]:
    """Extract function definitions from Python file"""
    functions = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find function definitions
            pattern = r'(?:async\s+)?def\s+(\w+)\s*\('
            matches = re.findall(pattern, content)
            functions.update(matches)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return functions

def extract_imports(filepath: Path) -> Set[str]:
    """Extract imported function names"""
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find import statements
            patterns = [
                r'from\s+[\w.]+\s+import\s+([\w,\s]+)',
                r'import\s+([\w.]+)',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Split comma-separated imports
                    names = [n.strip() for n in match.split(',')]
                    imports.update(names)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return imports

def find_function_calls(filepath: Path) -> Set[str]:
    """Find function calls in file"""
    calls = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find function calls
            pattern = r'(\w+)\s*\('
            matches = re.findall(pattern, content)
            calls.update(matches)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return calls

def analyze_backend_orphans(backend_dir: str):
    """Find potentially orphaned functions in backend"""
    print("\n" + "="*60)
    print(" BACKEND CODE ANALYSIS - ORPHANED FUNCTIONS")
    print("="*60)
    
    python_files = find_python_files(backend_dir)
    print(f"\nAnalyzing {len(python_files)} Python files...")
    
    # Collect all functions and calls
    all_functions = {}
    all_calls = set()
    all_imports = set()
    
    for filepath in python_files:
        functions = extract_functions(filepath)
        if functions:
            all_functions[filepath] = functions
        
        calls = find_function_calls(filepath)
        all_calls.update(calls)
        
        imports = extract_imports(filepath)
        all_imports.update(imports)
    
    # Find orphaned functions (defined but never called/imported)
    all_defined = set()
    for funcs in all_functions.values():
        all_defined.update(funcs)
    
    used_functions = all_calls | all_imports
    orphaned = all_defined - used_functions
    
    # Filter out common patterns that aren't orphans
    false_positives = {
        '__init__', '__str__', '__repr__', 'main', 'run', 'app',
        '__call__', '__enter__', '__exit__', 'get', 'post', 'put', 'delete'
    }
    orphaned = orphaned - false_positives
    
    if orphaned:
        print(f"\n⚠️  Found {len(orphaned)} potentially orphaned functions:\n")
        for func in sorted(orphaned):
            # Find which file defines it
            for filepath, funcs in all_functions.items():
                if func in funcs:
                    rel_path = filepath.relative_to(backend_dir)
                    print(f"  • {func:30} in {rel_path}")
                    break
    else:
        print("\n✓ No obvious orphaned functions found")

def analyze_api_endpoints(backend_main: str):
    """Analyze API endpoints and response structures"""
    print("\n" + "="*60)
    print(" API ENDPOINT ANALYSIS")
    print("="*60)
    
    try:
        with open(backend_main, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all endpoint definitions
        endpoint_pattern = r'@app\.(get|post|put|delete)\s*\("([^"]+)"'
        endpoints = re.findall(endpoint_pattern, content)
        
        if endpoints:
            print(f"\nFound {len(endpoints)} API endpoints:\n")
            
            methods_count = defaultdict(int)
            paths = []
            
            for method, path in endpoints:
                methods_count[method.upper()] += 1
                paths.append((method.upper(), path))
                print(f"  {method.upper():6} {path}")
            
            print(f"\nMethod distribution:")
            for method, count in sorted(methods_count.items()):
                print(f"  {method}: {count}")
        else:
            print("\nNo API endpoints found")
            
    except Exception as e:
        print(f"Error analyzing endpoints: {e}")

def analyze_response_models(backend_main: str):
    """Analyze Pydantic response models"""
    print("\n" + "="*60)
    print(" RESPONSE MODEL ANALYSIS")
    print("="*60)
    
    try:
        with open(backend_main, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find Pydantic models
        model_pattern = r'class\s+(\w+)\(BaseModel\):\s*\n\s*"""([^"]+)"""'
        models = re.findall(model_pattern, content)
        
        if models:
            print(f"\nFound {len(models)} Pydantic models:\n")
            for name, description in models:
                print(f"  • {name}")
                print(f"    {description.strip()}")
                print()
        
        # Find response_model usage
        response_model_pattern = r'response_model=(\w+)'
        response_models = re.findall(response_model_pattern, content)
        
        if response_models:
            print("Response models used in endpoints:")
            model_usage = defaultdict(int)
            for model in response_models:
                model_usage[model] += 1
            
            for model, count in sorted(model_usage.items()):
                print(f"  • {model}: {count} endpoints")
                
    except Exception as e:
        print(f"Error analyzing models: {e}")

def analyze_frontend_api_calls(frontend_dir: str):
    """Analyze what API endpoints the frontend uses"""
    print("\n" + "="*60)
    print(" FRONTEND API USAGE ANALYSIS")
    print("="*60)
    
    js_files = find_js_files(frontend_dir)
    print(f"\nAnalyzing {len(js_files)} JS/JSX files...")
    
    api_calls = set()
    
    for filepath in js_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find fetch/axios calls to API
            patterns = [
                r'fetch\s*\(\s*[`"\']([^`"\']+)[`"\']',
                r'axios\.\w+\s*\(\s*[`"\']([^`"\']+)[`"\']',
                r'(\/api\/[^`"\'\s]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                api_calls.update(matches)
                
        except Exception as e:
            pass
    
    if api_calls:
        print(f"\nFound {len(api_calls)} unique API endpoints used:\n")
        for call in sorted(api_calls):
            if call.startswith('/api/') or call.startswith('http'):
                print(f"  • {call}")
    else:
        print("\nNo API calls found")

def main():
    """Run all analyses"""
    backend_dir = "backend"
    frontend_dir = "frontend"
    backend_main = os.path.join(backend_dir, "main.py")
    
    print("\n" + "🔍 "*20)
    print(" "*15 + "TREE-SHAKE & API ANALYSIS")
    print("🔍 "*20)
    
    if os.path.exists(backend_dir):
        analyze_backend_orphans(backend_dir)
        
        if os.path.exists(backend_main):
            analyze_api_endpoints(backend_main)
            analyze_response_models(backend_main)
    else:
        print(f"\n❌ Backend directory not found: {backend_dir}")
    
    if os.path.exists(frontend_dir):
        analyze_frontend_api_calls(frontend_dir)
    else:
        print(f"\n❌ Frontend directory not found: {frontend_dir}")
    
    print("\n" + "="*60)
    print(" ANALYSIS COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
