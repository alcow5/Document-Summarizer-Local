#!/usr/bin/env python3
"""
Build script for Privacy-Focused AI Document Summarizer
Creates packaged distributions for Windows and macOS
"""

import os
import sys
import shutil
import subprocess
import platform
import json
from pathlib import Path
import argparse
import zipfile
from datetime import datetime
import requests
import tarfile

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"

BUILD_CONFIG = {
    "app_name": "DocumentSummarizer",
    "version": "1.0.0",
    "author": "Document Summarizer Team",
    "description": "Privacy-Focused AI Document Summarizer",
    "bundle_id": "com.documentsummarizer.app"
}


class BuildError(Exception):
    """Custom build error"""
    pass


class Builder:
    """Main builder class"""
    
    def __init__(self, platform_target=None, debug=False):
        self.platform = platform_target or platform.system().lower()
        self.debug = debug
        self.build_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create build directories
        self.build_dir = BUILD_DIR / self.build_timestamp
        self.dist_dir = DIST_DIR / self.build_timestamp
        
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.dist_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message, level="INFO"):
        """Simple logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command, cwd=None, capture_output=False):
        """Run shell command with error handling"""
        self.log(f"Running: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if capture_output:
                self.log(f"STDOUT: {e.stdout}", "ERROR")
                self.log(f"STDERR: {e.stderr}", "ERROR")
            raise BuildError(f"Command failed: {command}")
    
    def clean_build(self):
        """Clean previous build artifacts"""
        self.log("Cleaning previous builds...")
        
        # Clean backend build artifacts
        backend_build = BACKEND_DIR / "build"
        backend_dist = BACKEND_DIR / "dist"
        
        for dir_path in [backend_build, backend_dist]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.log(f"Removed {dir_path}")
        
        # Clean frontend build
        frontend_build = FRONTEND_DIR / "build"
        if frontend_build.exists():
            shutil.rmtree(frontend_build)
            self.log("Removed frontend build directory")
    
    def build_frontend(self):
        """Build the Electron frontend"""
        self.log("Building frontend...")
        
        # Install dependencies
        self.run_command("npm install", cwd=FRONTEND_DIR)
        
        # Build React app
        self.run_command("npm run build", cwd=FRONTEND_DIR)
        
        self.log("Frontend build completed")
    
    def build_backend(self):
        """Build the Python backend using PyInstaller"""
        self.log("Building backend...")
        
        # Create virtual environment if not exists
        venv_path = BACKEND_DIR / "venv"
        if not venv_path.exists():
            self.run_command(f"python -m venv {venv_path}", cwd=BACKEND_DIR)
        
        # Activate virtual environment and install dependencies
        if self.platform == "windows":
            activate_cmd = f"{venv_path}\\Scripts\\activate"
            pip_cmd = f"{venv_path}\\Scripts\\pip"
            python_cmd = f"{venv_path}\\Scripts\\python"
        else:
            activate_cmd = f"source {venv_path}/bin/activate"
            pip_cmd = f"{venv_path}/bin/pip"
            python_cmd = f"{venv_path}/bin/python"
        
        # Install dependencies
        self.run_command(f"{pip_cmd} install -r requirements.txt", cwd=BACKEND_DIR)
        self.run_command(f"{pip_cmd} install pyinstaller", cwd=BACKEND_DIR)
        
        # Create PyInstaller spec file
        spec_content = self._create_pyinstaller_spec()
        spec_file = BACKEND_DIR / "app.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Build with PyInstaller
        pyinstaller_cmd = f"{python_cmd} -m PyInstaller app.spec --clean"
        if not self.debug:
            pyinstaller_cmd += " --windowed"
        
        self.run_command(pyinstaller_cmd, cwd=BACKEND_DIR)
        
        self.log("Backend build completed")
    
    def _create_pyinstaller_spec(self):
        """Create PyInstaller spec file"""
        return f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['{BACKEND_DIR}'],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('../database/schema.sql', 'database/'),
        ('../models/', 'models/'),
    ],
    hiddenimports=[
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.protocols.websockets.auto',
        'sqlcipher3',
        'ollama',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{BUILD_CONFIG["app_name"]}-backend',
    debug={str(self.debug).lower()},
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={str(self.debug).lower()},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    def package_electron(self):
        """Package the Electron application"""
        self.log("Packaging Electron application...")
        
        # Copy backend executable to frontend resources
        backend_dist = BACKEND_DIR / "dist"
        backend_exe = None
        
        for file in backend_dist.iterdir():
            if file.is_file() and "backend" in file.name:
                backend_exe = file
                break
        
        if not backend_exe:
            raise BuildError("Backend executable not found")
        
        # Copy to frontend build
        frontend_resources = FRONTEND_DIR / "build" / "resources"
        frontend_resources.mkdir(exist_ok=True)
        shutil.copy2(backend_exe, frontend_resources)
        
        # Package with electron-builder
        if self.platform == "windows":
            self.run_command("npm run dist-win", cwd=FRONTEND_DIR)
        elif self.platform == "darwin":
            self.run_command("npm run dist-mac", cwd=FRONTEND_DIR)
        else:
            self.run_command("npm run dist", cwd=FRONTEND_DIR)
        
        self.log("Electron packaging completed")
    
    def create_installer(self):
        """Create platform-specific installer"""
        self.log("Creating installer...")
        
        frontend_dist = FRONTEND_DIR / "dist"
        
        if self.platform == "windows":
            installer_files = list(frontend_dist.glob("*.exe"))
        elif self.platform == "darwin":
            installer_files = list(frontend_dist.glob("*.dmg"))
        else:
            installer_files = list(frontend_dist.glob("*.AppImage"))
        
        if not installer_files:
            raise BuildError("No installer files found")
        
        # Copy installer to final distribution directory
        for installer in installer_files:
            final_name = f"{BUILD_CONFIG['app_name']}-{BUILD_CONFIG['version']}-{self.platform}{installer.suffix}"
            final_path = self.dist_dir / final_name
            shutil.copy2(installer, final_path)
            self.log(f"Created installer: {final_path}")
    
    def create_archive(self):
        """Create source code archive"""
        self.log("Creating source archive...")
        
        archive_name = f"{BUILD_CONFIG['app_name']}-{BUILD_CONFIG['version']}-source.zip"
        archive_path = self.dist_dir / archive_name
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add essential files
            essential_dirs = ['backend', 'frontend', 'database', 'docs']
            essential_files = ['README.md', 'LICENSE', '.gitignore']
            
            for dir_name in essential_dirs:
                dir_path = PROJECT_ROOT / dir_name
                if dir_path.exists():
                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file() and not self._should_exclude(file_path):
                            arcname = file_path.relative_to(PROJECT_ROOT)
                            zipf.write(file_path, arcname)
            
            for file_name in essential_files:
                file_path = PROJECT_ROOT / file_name
                if file_path.exists():
                    zipf.write(file_path, file_name)
        
        self.log(f"Created source archive: {archive_path}")
    
    def _should_exclude(self, file_path):
        """Check if file should be excluded from archive"""
        exclude_patterns = [
            'node_modules', '__pycache__', '.git', 'build', 'dist',
            '.env', '.DS_Store', '*.pyc', '*.log', 'venv'
        ]
        
        path_str = str(file_path).lower()
        return any(pattern in path_str for pattern in exclude_patterns)
    
    def generate_build_info(self):
        """Generate build information file"""
        build_info = {
            "app_name": BUILD_CONFIG["app_name"],
            "version": BUILD_CONFIG["version"],
            "build_date": datetime.now().isoformat(),
            "platform": self.platform,
            "debug": self.debug,
            "python_version": sys.version,
            "build_machine": platform.node()
        }
        
        info_file = self.dist_dir / "build_info.json"
        with open(info_file, 'w') as f:
            json.dump(build_info, f, indent=2)
        
        self.log(f"Generated build info: {info_file}")
    
    def build_all(self):
        """Run complete build process"""
        try:
            self.log(f"Starting build for {self.platform}")
            self.log(f"Build directory: {self.build_dir}")
            self.log(f"Distribution directory: {self.dist_dir}")
            
            # Build steps
            self.clean_build()
            self.build_frontend()
            self.build_backend()
            self.package_electron()
            self.create_installer()
            self.create_archive()
            self.generate_build_info()
            
            self.log("Build completed successfully!")
            self.log(f"Artifacts available in: {self.dist_dir}")
            
        except Exception as e:
            self.log(f"Build failed: {e}", "ERROR")
            sys.exit(1)


def download_ollama_binary():
    """Download appropriate Ollama binary for the target platform"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Map architecture names
    if arch in ['x86_64', 'amd64']:
        arch = 'amd64'
    elif arch in ['aarch64', 'arm64']:
        arch = 'arm64'
    
    # Ollama download URLs
    if system == 'windows':
        url = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"
        extract_to = "dist/ollama-windows/"
    elif system == 'darwin':  # macOS
        url = f"https://github.com/ollama/ollama/releases/latest/download/ollama-darwin-{arch}"
        extract_to = "dist/ollama-macos/"
    elif system == 'linux':
        url = f"https://github.com/ollama/ollama/releases/latest/download/ollama-linux-{arch}"
        extract_to = "dist/ollama-linux/"
    else:
        raise Exception(f"Unsupported platform: {system}")
    
    print(f"Downloading Ollama binary for {system} {arch}...")
    
    # Create directory
    Path(extract_to).mkdir(parents=True, exist_ok=True)
    
    # Download and extract
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        if url.endswith('.zip'):
            with open(f"{extract_to}/ollama.zip", 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            with zipfile.ZipFile(f"{extract_to}/ollama.zip", 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            os.remove(f"{extract_to}/ollama.zip")
        else:
            # Direct binary download
            with open(f"{extract_to}/ollama", 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            # Make executable on Unix systems
            if system != 'windows':
                os.chmod(f"{extract_to}/ollama", 0o755)
        
        print(f"✅ Ollama binary downloaded to {extract_to}")
    else:
        raise Exception(f"Failed to download Ollama: {response.status_code}")

def package_model(model_name="llama3:8b"):
    """Package the AI model for distribution"""
    print(f"Packaging model: {model_name}")
    
    # Create models directory
    models_dir = Path("dist/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Get Ollama model directory (platform specific)
    system = platform.system().lower()
    if system == 'windows':
        ollama_dir = Path.home() / ".ollama"
    elif system == 'darwin':
        ollama_dir = Path.home() / ".ollama"
    else:  # Linux
        ollama_dir = Path.home() / ".ollama"
    
    model_dir = ollama_dir / "models"
    
    if model_dir.exists():
        # Copy model files
        print(f"Copying model files from {model_dir}")
        shutil.copytree(model_dir, models_dir / "ollama_models", dirs_exist_ok=True)
        print(f"✅ Model {model_name} packaged")
    else:
        print(f"⚠️  Model directory not found: {model_dir}")
        print("Models will be downloaded on first run")

def build_backend():
    """Build backend with PyInstaller"""
    print("Building backend executable...")
    
    # PyInstaller command for backend
    cmd = [
        "pyinstaller",
        "--name=document-summarizer-backend",
        "--onefile",
        "--noconsole",
        "--add-data=config.yaml;.",
        "--add-data=../database/schema.sql;database/",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=uvicorn.lifespan.off",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=aiohttp",
        "app/main.py"
    ]
    
    subprocess.run(cmd, cwd="backend", check=True)
    print("✅ Backend built successfully")

def build_frontend():
    """Build frontend with Electron Builder"""
    print("Building frontend Electron app...")
    
    # Build React app first
    subprocess.run(["npm", "run", "build"], cwd="frontend", check=True)
    
    # Create electron main with Ollama integration
    create_electron_main_with_ollama()
    
    # Build Electron app
    subprocess.run(["npm", "run", "build-electron"], cwd="frontend", check=True)
    print("✅ Frontend built successfully")

def create_electron_main_with_ollama():
    """Create Electron main process with embedded Ollama management"""
    
    electron_main = '''
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess;
let ollamaProcess;

// Paths for bundled binaries
const isDev = process.env.NODE_ENV === 'development';
const resourcesPath = isDev ? process.cwd() : process.resourcesPath;

const getOllamaBinaryPath = () => {
  const platform = process.platform;
  if (platform === 'win32') {
    return path.join(resourcesPath, 'ollama-windows', 'ollama.exe');
  } else if (platform === 'darwin') {
    return path.join(resourcesPath, 'ollama-macos', 'ollama');
  } else {
    return path.join(resourcesPath, 'ollama-linux', 'ollama');
  }
};

const getBackendBinaryPath = () => {
  const platform = process.platform;
  const ext = platform === 'win32' ? '.exe' : '';
  return path.join(resourcesPath, `document-summarizer-backend${ext}`);
};

const startOllama = () => {
  return new Promise((resolve, reject) => {
    const ollamaBinary = getOllamaBinaryPath();
    
    if (!fs.existsSync(ollamaBinary)) {
      console.log('Ollama binary not found, using system Ollama');
      resolve();
      return;
    }
    
    console.log('Starting embedded Ollama...');
    
    // Set environment variables for embedded Ollama
    const env = { 
      ...process.env,
      OLLAMA_HOST: '127.0.0.1:11434',
      OLLAMA_MODELS: path.join(resourcesPath, 'models', 'ollama_models'),
      OLLAMA_HOME: path.join(app.getPath('userData'), 'ollama')
    };
    
    ollamaProcess = spawn(ollamaBinary, ['serve'], {
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    ollamaProcess.stdout.on('data', (data) => {
      console.log(`Ollama: ${data}`);
    });
    
    ollamaProcess.stderr.on('data', (data) => {
      console.log(`Ollama Error: ${data}`);
    });
    
    // Wait for Ollama to start
    setTimeout(() => {
      console.log('✅ Ollama started');
      resolve();
    }, 3000);
    
    ollamaProcess.on('error', (error) => {
      console.error('Failed to start Ollama:', error);
      reject(error);
    });
  });
};

const startBackend = () => {
  return new Promise((resolve, reject) => {
    const backendBinary = getBackendBinaryPath();
    
    if (!fs.existsSync(backendBinary)) {
      console.error('Backend binary not found:', backendBinary);
      reject(new Error('Backend binary not found'));
      return;
    }
    
    console.log('Starting backend...');
    
    const env = {
      ...process.env,
      PORT: '8050',
      HOST: '127.0.0.1'
    };
    
    backendProcess = spawn(backendBinary, [], {
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    backendProcess.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });
    
    backendProcess.stderr.on('data', (data) => {
      console.log(`Backend Error: ${data}`);
    });
    
    // Wait for backend to start
    setTimeout(() => {
      console.log('✅ Backend started');
      resolve();
    }, 5000);
    
    backendProcess.on('error', (error) => {
      console.error('Failed to start backend:', error);
      reject(error);
    });
  });
};

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    title: 'Privacy-Focused AI Document Summarizer',
    icon: path.join(__dirname, 'assets/icon.png')
  });

  // Load the React app
  const startUrl = isDev 
    ? 'http://localhost:3050' 
    : `file://${path.join(__dirname, '../build/index.html')}`;
  
  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

// App event handlers
app.whenReady().then(async () => {
  try {
    // Start services in sequence
    await startOllama();
    await startBackend();
    
    // Create main window
    createWindow();
    
    console.log('🚀 Application ready with embedded AI!');
    
  } catch (error) {
    console.error('Failed to start application:', error);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Cleanup on app quit
app.on('before-quit', () => {
  console.log('Shutting down services...');
  
  if (backendProcess) {
    backendProcess.kill();
  }
  
  if (ollamaProcess) {
    ollamaProcess.kill();
  }
});

// IPC handlers for communication with renderer
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-ai-status', async () => {
  // Check if services are running
  return {
    ollama: !!ollamaProcess,
    backend: !!backendProcess
  };
});
'''
    
    # Write the electron main file
    with open("frontend/electron.js", "w") as f:
        f.write(electron_main)
    
    print("✅ Electron main with Ollama integration created")

def update_package_json():
    """Update package.json for proper Electron building with resources"""
    
    package_json_additions = '''
{
  "main": "electron.js",
  "scripts": {
    "electron": "electron .",
    "electron-dev": "ELECTRON_IS_DEV=1 electron .",
    "build-electron": "electron-builder",
    "dist": "npm run build && electron-builder"
  },
  "build": {
    "appId": "com.privacy-ai.document-summarizer",
    "productName": "Privacy-Focused AI Document Summarizer",
    "directories": {
      "output": "dist"
    },
    "files": [
      "build/**/*",
      "electron.js",
      "assets/**/*"
    ],
    "extraResources": [
      {
        "from": "../dist/ollama-${os}",
        "to": "ollama-${os}",
        "filter": ["**/*"]
      },
      {
        "from": "../dist/models",
        "to": "models",
        "filter": ["**/*"]
      },
      {
        "from": "../backend/dist/document-summarizer-backend${/*}",
        "to": "."
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": "dmg",
      "icon": "assets/icon.icns"
    },
    "linux": {
      "target": "AppImage",
      "icon": "assets/icon.png"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
'''
    
    print("📝 Package.json configuration created for Electron Builder")
    print("Add the 'build' section to your frontend/package.json")

def main():
    """Main build process"""
    print("🚀 Starting Privacy-Focused AI Document Summarizer Build Process")
    print("=" * 60)
    
    try:
        # Step 1: Download Ollama binaries
        download_ollama_binary()
        
        # Step 2: Package AI models
        package_model("llama3:8b")
        
        # Step 3: Build backend
        build_backend()
        
        # Step 4: Build frontend
        build_frontend()
        
        # Step 5: Update configurations
        update_package_json()
        
        print("\n" + "=" * 60)
        print("🎉 BUILD COMPLETE!")
        print("=" * 60)
        print("✅ Ollama binary bundled")
        print("✅ AI models packaged")
        print("✅ Backend executable created")
        print("✅ Frontend Electron app built")
        print("\n📦 Your distributable app includes:")
        print("   • Complete AI processing (no internet required)")
        print("   • Encrypted local database")
        print("   • Professional desktop interface")
        print("   • One-click installer")
        
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 