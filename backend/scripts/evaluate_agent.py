import asyncio
import json
import os
import time
from pathlib import Path
from typing import Dict, Any

from backend.app.services.llm_provider import evaluate_communication
from backend.app.domain.evaluation import CommunicationEvaluation


CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "corpus"


async def evaluate_agentic_pipeline():
    print("Starting YC-Level Agentic Evaluation Pipeline...")
    if not CORPUS_DIR.exists():
        print(f"Corpus directory {CORPUS_DIR} not found. Please create it and add .json test cases.")
        return

    test_files = list(CORPUS_DIR.glob("*.json"))
    if not test_files:
        print(f"No .json test cases found in {CORPUS_DIR}.")
        return

    results = []
    total_latency = 0.0
    passed = 0
    total = len(test_files)

    for test_file in test_files:
        with open(test_file, "r") as f:
            test_case = json.load(f)
        
        print(f"\nEvaluating: {test_case.get('id', test_file.name)}")
        scenario = test_case.get("scenario", "Explain a technical project to a recruiter in 60 seconds.")
        audio_path_str = test_case.get("audio_path")
        
        if not audio_path_str:
            print("  Skipped: No audio_path provided in test case.")
            continue
            
        audio_path = CORPUS_DIR / audio_path_str
        if not audio_path.exists():
            print(f"  Skipped: Audio file {audio_path} not found.")
            continue
            
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            
        mime_type = "audio/wav" if audio_path.suffix == ".wav" else "audio/mp3"
        
        start_time = time.time()
        try:
            evaluation = evaluate_communication(audio_bytes, mime_type, scenario)
            latency = time.time() - start_time
            total_latency += latency
            
            # Check expected outcome
            expected = test_case.get("expected", {})
            expected_status = expected.get("evaluator_status")
            
            is_pass = True
            errors = []
            
            if expected_status and evaluation.evaluator_status != expected_status:
                is_pass = False
                errors.append(f"Status mismatch: expected {expected_status}, got {evaluation.evaluator_status}")
                
            if evaluation.evaluator_status == "completed":
                if not evaluation.evidence:
                    is_pass = False
                    errors.append("No evidence provided in completed evaluation.")
                
                expected_focus = expected.get("recommended_focus")
                if expected_focus and (not evaluation.recommended_focus or evaluation.recommended_focus[0] != expected_focus):
                    is_pass = False
                    errors.append(f"Focus mismatch: expected {expected_focus}, got {evaluation.recommended_focus}")
            
            if is_pass:
                passed += 1
                print(f"  [PASS] Latency: {latency:.2f}s")
            else:
                print(f"  [FAIL] Latency: {latency:.2f}s. Errors: {errors}")
                
            results.append({
                "id": test_case.get("id", test_file.name),
                "pass": is_pass,
                "latency": latency,
                "errors": errors,
                "output": evaluation.model_dump()
            })
            
        except Exception as e:
            latency = time.time() - start_time
            total_latency += latency
            print(f"  [ERROR] {str(e)}")
            results.append({
                "id": test_case.get("id", test_file.name),
                "pass": False,
                "latency": latency,
                "errors": [str(e)],
                "output": None
            })

    # Generate Report
    print("\n==============================================")
    print("        EVALUATION PIPELINE REPORT            ")
    print("==============================================")
    print(f"Total Tests: {total}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {total - passed}")
    print(f"Avg Latency: {(total_latency / total) if total else 0:.2f}s")
    
    report_md = f"""# Agentic Evaluation Pipeline Report

**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Model**: Gemini 2.5 Flash

## Summary
- **Total Tests**: {total}
- **Passed**: {passed}
- **Failed**: {total - passed}
- **Accuracy**: {(passed / total * 100) if total else 0:.1f}%
- **Average Latency**: {(total_latency / total) if total else 0:.2f}s

## Details
"""
    for r in results:
        status = "✅ PASS" if r["pass"] else "❌ FAIL"
        report_md += f"### {r['id']} - {status}\n"
        report_md += f"- Latency: {r['latency']:.2f}s\n"
        if not r["pass"]:
            report_md += f"- Errors: {', '.join(r['errors'])}\n"
        report_md += "\n"
        
    report_path = Path("evaluation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"\nDetailed report written to {report_path.absolute()}")


if __name__ == "__main__":
    asyncio.run(evaluate_agentic_pipeline())
