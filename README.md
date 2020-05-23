# Better Job Search

Better Job Search is a quick and dirty web scraper for one of the more popular job search websites. I'd tell you what it is, but this project would like go against their terms and conditions. I haven't even referenced it in the source code. **However**, if you can guess the name, you can put it in the config file and it should work fine. At least until they change their layout or something.

## Why not just use their API?

Their API is only available to enterprise customers as far as I know, at least for that aspect of their site. I'm not enterprise.

## Requirements

* Python 3
* pip

## Installation

First, clone the repo, then:

```
cd better-job-search
pip install -r requirements.txt
cp config.py.sample config.py
```

Then edit config.py:

* **site_name**: the bit that would go between *www* and *.com*
* **keyword_list**: a list of the keywords of jobs you want to hunt for
* **country_blacklist**: where *don't* you want to work?
* **language_whitelist**: only find postings in this language
* **strict_search**: If true, only return jobs where your keywords are in the job title. Otherwise return all jobs sent by the job site

Finally:

```
python jobs.py
```

Once that's finished running you should find `output.html` in the better-job-search directory. Open it in your browser to view your job listings.

## Help! It's Broken!

It's likely because the job site changed their layout or CSS names or something. Since this is just a quick and dirty script, I'm not likely to spend much time maintaining it after I've stopped using it myself, so you may have to dig around in the code and change things as needed. Don't forget to make pull request if you do so!
