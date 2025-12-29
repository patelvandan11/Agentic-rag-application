import os
import re
import urllib.request




def extract_arxiv_id(url: str) -> str:
    """
    Extract arXiv ID from any valid arXiv URL
    """
    # Matches: 2303.12345 or 2303.12345v2
    match = re.search(r"(\d{4}\.\d{4,5}(v\d+)?)", url)

    if not match:
        raise ValueError("Could not extract arXiv ID from URL")

    return match.group(1)


def download_arxiv_pdf(arxiv_url: str, save_dir: str) -> str:
    """
    Download arXiv PDF from any arXiv URL
    """
    arxiv_id = extract_arxiv_id(arxiv_url)

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{arxiv_id}.pdf")

    urllib.request.urlretrieve(pdf_url, file_path)

    return file_path


