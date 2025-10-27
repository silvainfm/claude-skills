#!/usr/bin/env python3
"""
Test setup scripts for correctness and path validation.

Tests that bash scripts reference correct paths and are syntactically valid.
"""

import subprocess
import re
from pathlib import Path
import pytest


class TestSetupMCPScript:
    """Test setup_mcp.sh for path correctness and syntax"""

    @pytest.fixture
    def script_path(self):
        """Get path to setup_mcp.sh"""
        return Path("setup_mcp.sh")

    @pytest.fixture
    def script_content(self, script_path):
        """Read setup_mcp.sh content"""
        with open(script_path, 'r') as f:
            return f.read()

    def test_setup_mcp_exists(self, script_path):
        """Test that setup_mcp.sh exists"""
        assert script_path.exists(), "setup_mcp.sh should exist"
        assert script_path.is_file(), "setup_mcp.sh should be a file"

    def test_bash_syntax_valid(self, script_path):
        """Test that setup_mcp.sh has valid bash syntax"""
        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Bash syntax error: {result.stderr}"

    def test_references_correct_mcp_directory(self, script_content):
        """Test that script references skill_seeker_mcp/ not old mcp/ directory"""
        # Should NOT reference old mcp/ directory
        old_refs = re.findall(r'(?:^|[^a-z_])mcp/(?!\.json)', script_content, re.MULTILINE)
        assert len(old_refs) == 0, f"Found {len(old_refs)} references to old 'mcp/' directory: {old_refs}"

        # SHOULD reference skill_seeker_mcp/
        new_refs = re.findall(r'skill_seeker_mcp/', script_content)
        assert len(new_refs) >= 6, f"Expected at least 6 references to 'skill_seeker_mcp/', found {len(new_refs)}"

    def test_requirements_txt_path(self, script_content):
        """Test that requirements.txt path is correct"""
        assert "skill_seeker_mcp/requirements.txt" in script_content, \
            "Should reference skill_seeker_mcp/requirements.txt"
        # Check for old mcp/ directory (but not skill_seeker_mcp/)
        import re
        old_refs = re.findall(r'(?<!skill_seeker_)mcp/requirements\.txt', script_content)
        assert len(old_refs) == 0, \
            f"Should NOT reference old 'mcp/requirements.txt' (found {len(old_refs)}): {old_refs}"

    def test_server_py_path(self, script_content):
        """Test that server.py path is correct"""
        import re
        assert "skill_seeker_mcp/server.py" in script_content, \
            "Should reference skill_seeker_mcp/server.py"
        # Check for old mcp/ directory (but not skill_seeker_mcp/)
        old_refs = re.findall(r'(?<!skill_seeker_)mcp/server\.py', script_content)
        assert len(old_refs) == 0, \
            f"Should NOT reference old 'mcp/server.py' (found {len(old_refs)}): {old_refs}"

    def test_referenced_files_exist(self):
        """Test that all files referenced in setup_mcp.sh actually exist"""
        # Check critical paths
        assert Path("skill_seeker_mcp/requirements.txt").exists(), \
            "skill_seeker_mcp/requirements.txt should exist"
        assert Path("skill_seeker_mcp/server.py").exists(), \
            "skill_seeker_mcp/server.py should exist"

    def test_config_directory_exists(self):
        """Test that referenced config directory exists"""
        assert Path("configs/").exists(), "configs/ directory should exist"
        assert Path("configs/").is_dir(), "configs/ should be a directory"

    def test_script_is_executable(self, script_path):
        """Test that setup_mcp.sh is executable"""
        import os
        assert os.access(script_path, os.X_OK), "setup_mcp.sh should be executable"

    def test_json_config_path_format(self, script_content):
        """Test that JSON config examples use correct format"""
        # Check for the config path format in the script
        assert '"$REPO_PATH/skill_seeker_mcp/server.py"' in script_content, \
            "Config should show correct server.py path with $REPO_PATH variable"

    def test_no_hardcoded_paths(self, script_content):
        """Test that script doesn't contain hardcoded absolute paths"""
        # Check for suspicious absolute paths (but allow $REPO_PATH and ~/.config)
        hardcoded_paths = re.findall(r'(?<![$~])/mnt/[^\s"\']+', script_content)
        assert len(hardcoded_paths) == 0, f"Found hardcoded absolute paths: {hardcoded_paths}"

    def test_pytest_command_references(self, script_content):
        """Test that pytest commands reference correct test files"""
        # Check for test file references
        if "pytest" in script_content:
            assert "tests/test_mcp_server.py" in script_content, \
                "Should reference correct test file path"


class TestBashScriptGeneral:
    """General tests for all bash scripts in repository"""

    @pytest.fixture
    def all_bash_scripts(self):
        """Find all bash scripts in repository root"""
        root = Path(".")
        return list(root.glob("*.sh"))

    def test_all_scripts_have_shebang(self, all_bash_scripts):
        """Test that all bash scripts have proper shebang"""
        for script in all_bash_scripts:
            with open(script, 'r') as f:
                first_line = f.readline()
            assert first_line.startswith("#!"), f"{script} should have shebang"
            assert "bash" in first_line.lower(), f"{script} should use bash"

    def test_all_scripts_syntax_valid(self, all_bash_scripts):
        """Test that all bash scripts have valid syntax"""
        for script in all_bash_scripts:
            result = subprocess.run(
                ["bash", "-n", str(script)],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, \
                f"{script} has syntax error: {result.stderr}"

    def test_all_scripts_use_set_e(self, all_bash_scripts):
        """Test that scripts use 'set -e' for error handling"""
        for script in all_bash_scripts:
            with open(script, 'r') as f:
                content = f.read()
            # Check for set -e or set -o errexit
            has_error_handling = (
                re.search(r'set\s+-[a-z]*e', content) or
                re.search(r'set\s+-o\s+errexit', content)
            )
            assert has_error_handling, \
                f"{script} should use 'set -e' for error handling"

    def test_no_deprecated_backticks(self, all_bash_scripts):
        """Test that scripts use $() instead of deprecated backticks"""
        for script in all_bash_scripts:
            with open(script, 'r') as f:
                content = f.read()
            # Allow backticks in comments
            lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
            code_content = '\n'.join(lines)
            backticks = re.findall(r'`[^`]+`', code_content)
            assert len(backticks) == 0, \
                f"{script} uses deprecated backticks: {backticks}. Use $() instead"


class TestMCPServerPaths:
    """Test that MCP server references are consistent across codebase"""

    def test_github_workflows_reference_correct_paths(self):
        """Test that GitHub workflows reference correct MCP paths"""
        workflow_file = Path(".github/workflows/tests.yml")
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                content = f.read()
            # Should NOT reference old mcp/ directory
            assert "mcp/requirements.txt" not in content or "skill_seeker_mcp/requirements.txt" in content, \
                "GitHub workflow should use correct MCP paths"

    def test_readme_references_correct_paths(self):
        """Test that README references correct MCP paths"""
        readme = Path("README.md")
        if readme.exists():
            with open(readme, 'r') as f:
                content = f.read()
            # Check for old mcp/ directory paths (but allow mcp.json and "mcp" package name)
            # Use negative lookbehind to exclude skill_seeker_mcp/
            old_mcp_refs = re.findall(r'(?<!skill_seeker_)mcp/(server\.py|requirements\.txt)', content)
            if len(old_mcp_refs) > 0:
                pytest.fail(f"README references old mcp/ directory: {old_mcp_refs}")

    def test_documentation_references_correct_paths(self):
        """Test that documentation files reference correct MCP paths"""
        doc_files = list(Path("docs/").glob("*.md")) if Path("docs/").exists() else []
        for doc_file in doc_files:
            with open(doc_file, 'r') as f:
                content = f.read()
            # Check for old mcp/ directory paths (but allow mcp.json and "mcp" package name)
            old_mcp_refs = re.findall(r'(?<!skill_seeker_)mcp/(server\.py|requirements\.txt)', content)
            if len(old_mcp_refs) > 0:
                pytest.fail(f"{doc_file} references old mcp/ directory: {old_mcp_refs}")


def test_mcp_directory_structure():
    """Test that MCP directory structure is correct"""
    mcp_dir = Path("skill_seeker_mcp")
    assert mcp_dir.exists(), "skill_seeker_mcp/ directory should exist"
    assert mcp_dir.is_dir(), "skill_seeker_mcp should be a directory"
    assert (mcp_dir / "server.py").exists(), "skill_seeker_mcp/server.py should exist"
    assert (mcp_dir / "requirements.txt").exists(), "skill_seeker_mcp/requirements.txt should exist"

    # Old directory should NOT exist
    old_mcp = Path("mcp")
    if old_mcp.exists():
        # If it exists, it should not contain server.py (might be leftover empty dir)
        assert not (old_mcp / "server.py").exists(), \
            "Old mcp/server.py should not exist - directory was renamed to skill_seeker_mcp/"


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Setup Scripts")
    print("=" * 60)
    pytest.main([__file__, "-v"])
