import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def extract_abstract(article_url):
    """Attempts to extract the abstract from an article page."""
    try:
        response = requests.get(article_url, timeout=10)
        if response.status_code != 200:
            if response.status_code == 403:
                #some sites block scraping
                return "Forbitten 403"
            else:
                return "Abstract not found"

        soup = BeautifulSoup(response.text, "html.parser")

        # Define possible abstract locations
        abstract_selectors = [
            'section#abstract div[role="paragraph"]',  # Example 1
            'div.c-article-section__content',  # Example 2
            'section#abstract p',  # Example 3
            'div.Abstract__block__text p',  # Example 4
            'div.abstract',  # Generic case
            'p.abstract',  # Another possible case
        ]

        # Try each selector
        for selector in abstract_selectors:
            abstract_element = soup.select_one(selector)
            if abstract_element:
                return abstract_element.get_text(strip=True)

        return "Abstract not found"

    except Exception as e:
        return f"Error fetching abstract: {str(e)}"

def scrape_scholar_articles(query, num_pages, year_low, year_high):
    articles = []
    page = 0
    while page < num_pages:
        url = f"https://scholar.google.com/scholar?start={page*10}&q={query}&hl=el&as_ylo={year_low}&as_yhi={year_high}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("div", class_="gs_ri")

        for result in results:
            title = result.find("h3", class_="gs_rt").text
            authors = result.find("div", class_="gs_a").text
            link = result.find("a")["href"]
            abstract = extract_abstract(link)  # Extract abstract

            articles.append({
                "Title": title,
                "Authors": authors,
                "Link": link,
                "Abstract": abstract
            })

        page += 1

    return articles

def save_to_excel(articles, filename):
    df = pd.DataFrame(articles)
    df.to_excel(filename, index=False)

def browse_folder():
    folder_path = filedialog.askdirectory()
    entry_folder.delete(0, tk.END)
    entry_folder.insert(tk.END, folder_path)

def scrape_articles():
    query = entry_query.get()
    num_pages = int(entry_pages.get())
    year_low = int(year1.get())
    year_high = int(year2.get())

    articles = scrape_scholar_articles(query, num_pages, year_low, year_high)

    folder_path = entry_folder.get()
    if folder_path:
        filename = f"{folder_path}/scholar_articles.xlsx"
    else:
        filename = "scholar_articles.xlsx"

    save_to_excel(articles, filename)
    label_status.config(text="Extraction complete. Data saved to scholar_articles.xlsx.")

# Create the main window
window = tk.Tk()
window.title("Google Scholar Scraper")
window.geometry("400x300")

# Create input fields and labels
label_query = tk.Label(window, text="Article Title or Keyword:")
label_query.pack()
entry_query = tk.Entry(window, width=40)
entry_query.pack()

label_pages = tk.Label(window, text="Number of Pages:")
label_pages.pack()
entry_pages = tk.Entry(window, width=40)
entry_pages.pack()

# Year range section
label_years = tk.Label(window, text="Year range of results:")
label_years.pack()

frame_years = tk.Frame(window)  # Frame to hold the year inputs
frame_years.pack()

label_from = tk.Label(frame_years, text="From:")
label_from.grid(row=0, column=0, padx=5)

year1 = tk.Entry(frame_years, width=10)
year1.grid(row=0, column=1, padx=5)

label_till = tk.Label(frame_years, text="Till:")
label_till.grid(row=0, column=2, padx=5)

year2 = tk.Entry(frame_years, width=10)
year2.grid(row=0, column=3, padx=5)

# Folder Section
label_folder = tk.Label(window, text="Output Folder (optional):")
label_folder.pack()
entry_folder = tk.Entry(window, width=40)
entry_folder.pack()

# Create browse button
button_browse = tk.Button(window, text="Browse", command=browse_folder)
button_browse.pack()

# Create extract button
button_extract = tk.Button(window, text="Extract Data", command=scrape_articles)
button_extract.pack()

# Create status label
label_status = tk.Label(window, text="")
label_status.pack()

# Run the main window loop
window.mainloop()
