# Path shim for direct execution support
import sys
from pathlib import Path

if __name__ == "__main__":
    # Add the project root to sys.path so absolute imports work when run directly
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

import argparse
import json

from src.config import SETTINGS
from src.eligibility import evaluate_eligibility
from src.github_enrichment import enrich_candidate, parse_github_username
from src.parser import parse_resume_directory
from src.scoring import score_candidate


def process_resume_batch(input_dir: str, output_path: str) -> dict:
    profiles, summary = parse_resume_directory(input_dir)
    results = []
    eligible_count = 0
    rejected_count = 0

    for profile in profiles:
        try:
            eligibility = evaluate_eligibility(profile)
            print(f"Processing {profile.name}...", end=" ")
            if eligibility["eligible"]:
                eligible_count += 1
                github_signal = enrich_candidate({"github_url": profile.github_url})
                scored = score_candidate(profile, eligibility, github_signal)
                scored["candidate_name"] = profile.name
                results.append(scored)
                print(f"eligible, score {scored['total_score']}")
            else:
                rejected_count += 1
                rejected = {
                    "rank": None,
                    "candidate_name": profile.name,
                    "eligible": False,
                    "total_score": 0,
                    "score_breakdown": {},
                    "matched_skills": eligibility.get("matched_skills", []),
                    "project_summary": (" ".join(profile.projects)[:500] if profile.projects else "No project details found."),
                    "github_summary": "N/A",
                    "strengths": [],
                    "concerns": [],
                    "rejection_reasons": eligibility.get("rejection_reasons", []),
                }
                results.append(rejected)
                print("rejected")
        except Exception as exc:
            print(f"Error processing {profile.name}: {exc}")

    eligible_results = [item for item in results if item.get("eligible")]
    eligible_results.sort(key=lambda item: item.get("total_score", 0), reverse=True)
    for idx, item in enumerate(eligible_results, start=1):
        item["rank"] = idx

    batch_summary = {
        "total_resumes": summary["total"],
        "successfully_parsed": summary["parsed"],
        "eligible": eligible_count,
        "rejected": rejected_count,
        "failed": summary["failed"],
    }

    output = {
        "summary": batch_summary,
        "candidates": results,
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"\nBatch summary: {json.dumps(batch_summary, indent=2)}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Resume Screening and Ranking")
    parser.add_argument("--input", default=SETTINGS.INPUT_DIR, help="Folder containing resume PDFs")
    parser.add_argument("--output", default=SETTINGS.OUTPUT_PATH, help="Path for the JSON result output")
    args = parser.parse_args()
    process_resume_batch(args.input, args.output)


if __name__ == "__main__":
    main()
