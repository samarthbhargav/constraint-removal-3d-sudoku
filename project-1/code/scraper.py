
# coding: utf-8

# In[19]:


import requests
import os
import bs4
import numpy as np


# In[83]:


START, END = 1, 5354
DOWNLOAD_DIR = "./scraped/"
PUZZLE_DIR = "./puzzles"
URL = "http://www.menneske.no/sudoku3d/eng/showpuzzle.html?number={}"
for index in range(START, END + 1):
    path = os.path.join(DOWNLOAD_DIR, "{}.html".format(index))
    if os.path.exists(path):
        continue
    print("Downloading {} to {}".format(index, path))
    response = requests.get(URL.format(index))
    if response.status_code != 200:
        print("Couldn't get {} :(".format(index))
        continue
    
    with  open(path, "w") as writer:
        writer.write(response.text)
    print("Saved file {}".format(path))


# In[89]:


def parse_html(puzzle_no):
    numbers = list("123456789")
    with open(os.path.join(DOWNLOAD_DIR, "{}.html".format(puzzle_no))) as reader:
        html = reader.read()
    
    soup = bs4.BeautifulSoup(html)
    grids = soup.findAll("div", { "class" : "grid" })
    assert len(grids) == 9

    puzzle = np.zeros((9, 9, 9))
    data = []
    for grid in grids:
        children = [_ for _ in grid.children]
        assert len(children) == 3
        grid_number = int(children[-2].split(":")[-1].strip())
        # the grids are one-indexed, while we are using 0-indexed data
        grid_number -= 1

        sub_grids = children[0].findAll("tr")
        assert len(sub_grids) == 9
        for grid_index, sub in enumerate(sub_grids):
            tds = sub.findAll("td")
            assert len(tds) == 9
            for index, element in enumerate(tds):
                number = next(element.children).strip()
                if number in numbers:
                    puzzle[grid_number, grid_index, index] = int(number)
                    data.append((grid_number, grid_index, index, int(number)))
    with open(os.path.join(PUZZLE_DIR, "{}.txt".format(puzzle_no)), "w") as writer:
        for d in data:
            writer.write("{}\n".format(",".join(str(_) for _ in d)))

for index in range(START, END + 1):
    parse_html(index)

