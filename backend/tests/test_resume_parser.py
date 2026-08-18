from __future__ import annotations

import json
from pathlib import Path

from app.services.resume_parser import (
    extract_resume_text,
    _basic_parse,
    extract_text_from_txt,
)


class TestExtractResumeText:
    def test_txt_extraction(self, tmp_path: Path):
        resume = tmp_path / "resume.txt"
        resume.write_text("John Doe\nDevOps Engineer\nAWS, Kubernetes, Terraform")
        result = extract_text_from_txt(resume)
        assert "John Doe" in result
        assert "DevOps Engineer" in result

    def test_unsupported_format(self, tmp_path: Path):
        resume = tmp_path / "resume.xyz"
        resume.write_text("test")
        result = extract_resume_text(resume)
        assert result == ""

    def test_empty_txt(self, tmp_path: Path):
        resume = tmp_path / "empty.txt"
        resume.write_text("")
        result = extract_text_from_txt(resume)
        assert result == ""


class TestBasicParse:
    def test_basic_parse_returns_structure(self):
        text = "Jane Smith\nSenior DevOps Engineer\nAWS, Kubernetes, Terraform\n5 years experience"
        result = _basic_parse(text)
        assert "full_name" in result
        assert "technologies" in result
        assert "aws_experience" in result
        assert result["full_name"] == "Jane Smith"

    def test_basic_parse_empty(self):
        result = _basic_parse("")
        assert result["full_name"] == ""
        assert result["technologies"] == []
