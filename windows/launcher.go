// Windows .exe launcher — opens a file picker for .ipynb/.py files, then runs
// with uvx juv run (Jupyter), uvx marimo edit --sandbox (marimo), or uv run (plain .py).

package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func main() {
	exe, err := os.Executable()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	exeDir := filepath.Dir(exe)

	// Check if exactly one notebook exists next to the .exe (skip picker if so)
	notebook := ""
	entries, _ := os.ReadDir(exeDir)
	var matches []string
	for _, e := range entries {
		if strings.HasSuffix(e.Name(), ".ipynb") || strings.HasSuffix(e.Name(), ".py") {
			matches = append(matches, e.Name())
		}
	}
	if len(matches) == 1 {
		notebook = matches[0]
	}

	notebookDir := exeDir

	if notebook == "" {
		// Show file picker for .ipynb and .py files
		out, err := exec.Command("powershell", "-NoProfile", "-Command", `
			Add-Type -AssemblyName System.Windows.Forms
			$dlg = New-Object System.Windows.Forms.OpenFileDialog
			$dlg.Title = "Select a notebook (.ipynb or .py)"
			$dlg.Filter = "Notebooks (*.ipynb;*.py)|*.ipynb;*.py|Jupyter Notebooks (*.ipynb)|*.ipynb|Python Scripts (*.py)|*.py"
			$dlg.InitialDirectory = [Environment]::GetFolderPath('UserProfile')
			if ($dlg.ShowDialog() -eq 'OK') { $dlg.FileName } else { "" }
		`).Output()
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error showing file dialog: %v\n", err)
			os.Exit(1)
		}

		selected := strings.TrimSpace(string(out))
		if selected == "" {
			os.Exit(0)
		}

		notebookDir = filepath.Dir(selected)
		notebook = filepath.Base(selected)
	}

	// Choose the right command based on file extension (and marimo dependency for .py)
	runCmd := "uvx juv run"
	if strings.HasSuffix(notebook, ".py") {
		content, _ := os.ReadFile(filepath.Join(notebookDir, notebook))
		if strings.Contains(string(content), `"marimo`) {
			runCmd = "uvx marimo edit --sandbox"
		} else {
			runCmd = "uv run"
		}
	}

	// Bootstrap uv if needed, then run
	tmpDir := os.TempDir()
	script := fmt.Sprintf(`@echo off
where uv >nul 2>&1 || (
    echo Installing uv...
    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
)
cd /d "%s"
echo Launching %s ...
%s "%s"
pause
`, notebookDir, notebook, runCmd, notebook)

	batPath := filepath.Join(tmpDir, "notebook-launcher-run.bat")
	os.WriteFile(batPath, []byte(script), 0644)

	cmd := exec.Command("cmd", "/c", batPath)
	cmd.Dir = notebookDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin
	cmd.Run()

	os.Remove(batPath)
}
