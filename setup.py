from setuptools import setup

setup(
    name="youtube_mp3_downloader",
    version="1.0",
    description="A YouTube to MP3 Downloader",
    author="SWORD-SAINT",
    author_email="gotuhamsankar@aol.com",
    packages=["youtube_mp3_downloader"],  # Replace with your package name
    install_requires=[
        "requests",
        "pytube",
        "Pillow",
    ],
    entry_points={
        "console_scripts": [
            "youtube-mp3-downloader = youtube_mp3_downloader:main",  # Replace with your module and main function
        ]
    },
)
