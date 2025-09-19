<!-- ABOUT THE PROJECT -->
## About The Project

A small scraper of potentially useful song fields from the [VocaDB](https://vocadb.net/) website with functionality for scraping the views count for each song vide url (and more).

Created with the intention of using PostgreSQL as a database (due to the amount and format of data from VocaDB).

This project can theoretically be expanded to scrape other fields as well.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* Python 3.12.10
* Jupyter Notebook 7.2.1
* PostgreSQL 17.5

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

This section will guide you through installing requirements for this project. I have not tested it outside of my system and outside of the program versions I have specified, so I do not know if it will work on earlier versions.

### Prerequisites

1. Install Python 3.8+: https://docs.python.org/3/using/index.html
2. Install Jupyter Notebook: https://jupyter.org/install
3. Install PostgreSQL: https://www.postgresql.org/docs/current/installation.html

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/amiadesu/VocaDBScraper.git
   ```
2. Install requirements
   ```sh
   pip install -r requirements.txt
   ```
3. Create your own `.env` from `.env.example`
4. (Optional, but recommended) Get a YouTube API key by following this guide: https://developers.google.com/youtube/v3/getting-started

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Once you installed all requirements, you should run a `main.py` script to get an initial `songs` and `songurls` tables inside you database.

After `main.py` stops it's execution, you can (if you need) open views.ipynb and start scraping views count for all URLs inside `songurls` table if the service of URL is supported.

After you retrieve all views count you will need to merge data from `songurls` and `songs` tables. You can do it using the very bottom section inside `views.ipynb`.

Notice, that you can just run all cells inside `views.ipynb` and it will do all the work automatically in sequential order if no problems will occure.

_You can find dataset example at [Kaggle](...)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Add support for SoundCloud service
- [ ] Add support for Piapro service
- [ ] Add support for Bandcamp service

See the [open issues](https://github.com/amiadesu/VocaDBScraper/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/amiadesu/VocaDBScraper/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=amiadesu/VocaDBScraper" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the MIT. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
