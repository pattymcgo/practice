"""
scrape_bookstore.py
-------------------
Automatically scrapes textbook info from the BMCC bookstore website
using Selenium (a tool that controls a real Chrome browser).

Loops through every department, course, and section for a chosen term,
collects all textbook data, and saves it to an Excel file.

HOW TO RUN:
    python scrape_bookstore.py

REQUIREMENTS:
    pip install selenium undetected-chromedriver openpyxl pandas
"""

import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# ── Settings ──────────────────────────────────────────────────────────────────

BOOKSTORE_URL = "https://www.bkstr.com/bmccstore/shop/textbooks-and-course-materials"
WAIT_TIMEOUT = 20
SHORT_PAUSE = 1.5
LONG_PAUSE = 3.0

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_dropdown(driver, name, min_options=2, timeout=WAIT_TIMEOUT):
    """
    Waits for a <select> with the given name to have at least min_options options.
    Returns a Select object, or None if it times out.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(Select(d.find_element(By.NAME, name)).options) >= min_options
        )
        return Select(driver.find_element(By.NAME, name))
    except (TimeoutException, NoSuchElementException):
        return None


def real_options(dropdown):
    """Returns options that are real values (not placeholder 'Select ...' entries)."""
    return [o for o in dropdown.options
            if o.get_attribute("value") and not o.text.lower().startswith("select")]


def extract_text(parent, css):
    """Returns text of the first matching element, or empty string if not found."""
    try:
        return parent.find_element(By.CSS_SELECTOR, css).text.strip()
    except NoSuchElementException:
        return ""


def human_pause(min_sec=1.0, max_sec=2.5):
    """Waits a random amount of time — makes the script look less robotic."""
    time.sleep(random.uniform(min_sec, max_sec))


def check_for_bot_block(driver):
    """
    Checks if the site is showing a bot-detection page.
    If detected, pauses and asks the user to solve it manually before continuing.
    """
    page_text = driver.page_source.lower()
    if "verify you are a human" in page_text or "access denied" in page_text or "automation" in page_text:
        print("\n[!] Bot detection triggered.")
        print("    Please solve the challenge in the browser window.")
        input("    Press Enter here once you've passed it and the page looks normal...")
        time.sleep(LONG_PAUSE)


# ── Main ──────────────────────────────────────────────────────────────────────

def scrape_bookstore():
    print("Opening Chrome browser...")
    driver = uc.Chrome()
    driver.maximize_window()
    driver.get(BOOKSTORE_URL)
    time.sleep(LONG_PAUSE)
    check_for_bot_block(driver)

    try:
        _run_scraper(driver)
    except Exception as e:
        print(f"\n[ERROR] Something went wrong: {e}")
        print("The browser will stay open so you can see what happened.")
        input("Press Enter to close the browser...")
    finally:
        driver.quit()


def _run_scraper(driver):
    """The actual scraping logic — separated so errors don't silently close the browser."""

    # --- Select program: BMCC ---
    program_dropdown = get_dropdown(driver, "programdropdown")
    if program_dropdown is None:
        print("[ERROR] Could not find the program dropdown.")
        return
    program_dropdown.select_by_visible_text("BMCC")
    print("Selected program: BMCC")
    human_pause()

    # --- Select term ---
    term_dropdown = get_dropdown(driver, "termdropdown")
    if term_dropdown is None:
        print("[ERROR] Could not find the term dropdown.")
        return

    term_options = real_options(term_dropdown)
    print("\nAvailable terms:")
    for i, o in enumerate(term_options):
        print(f"  {i + 1}. {o.text}")

    while True:
        choice = input("\nEnter the number of the term to scrape: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(term_options):
            selected_term = term_options[int(choice) - 1]
            break
        print("  Please enter a valid number.")

    # Save as plain strings immediately — option elements go stale after page updates
    selected_term_text = selected_term.text
    selected_term_value = selected_term.get_attribute("value")

    term_dropdown = get_dropdown(driver, "termdropdown")
    term_dropdown.select_by_value(selected_term_value)
    print(f"Selected term: {selected_term_text}")
    human_pause(2, 4)
    check_for_bot_block(driver)

    # --- Get all departments ---
    dept_dropdown = get_dropdown(driver, "searchDepartment0")
    if dept_dropdown is None:
        print("[ERROR] Department dropdown did not load.")
        return

    dept_options = real_options(dept_dropdown)
    dept_names = [o.text for o in dept_options]
    print(f"Found {len(dept_names)} departments.\n")

    all_textbooks = []
    first_search = True  # Used to run a one-time diagnostic on the results page

    # --- Loop: department → course → section ---
    for dept_i, dept_name in enumerate(dept_names):
        print(f"[{dept_i + 1}/{len(dept_names)}] {dept_name}")
        check_for_bot_block(driver)

        dept_dropdown = get_dropdown(driver, "searchDepartment0")
        if dept_dropdown is None:
            print(f"  [!] Department dropdown gone. Skipping {dept_name}.")
            continue
        dept_dropdown.select_by_visible_text(dept_name)
        human_pause(2, 4)

        course_dropdown = get_dropdown(driver, "selectedCourse0")
        if course_dropdown is None:
            print(f"  [!] No courses loaded for {dept_name}.")
            continue

        course_names = [o.text for o in real_options(course_dropdown)]
        if not course_names:
            print(f"  [!] No courses for {dept_name}.")
            continue

        for course_name in course_names:
            course_dropdown = get_dropdown(driver, "selectedCourse0")
            if course_dropdown is None:
                continue
            course_dropdown.select_by_visible_text(course_name)
            human_pause(2, 4)

            section_dropdown = get_dropdown(driver, "selectedSection0")
            if section_dropdown is None:
                continue

            section_names = [o.text for o in real_options(section_dropdown)]
            if not section_names:
                continue

            for section_name in section_names:
                section_dropdown = get_dropdown(driver, "selectedSection0")
                if section_dropdown is None:
                    continue
                section_dropdown.select_by_visible_text(section_name)
                human_pause()

                clicked = click_search_button(driver)
                if not clicked:
                    print(f"  [!] Could not find search button for {dept_name} {course_name} {section_name}")
                    if first_search:
                        diagnose_buttons(driver)
                        input("Press Enter to continue...")
                    continue

                human_pause(2, 4)
                check_for_bot_block(driver)

                # One-time diagnostic on first result to identify book elements
                if first_search:
                    diagnose_results(driver)
                    input("\nPress Enter to continue scraping...")
                    first_search = False

                books = scrape_results(driver, selected_term_text, dept_name, course_name, section_name)
                all_textbooks.extend(books)
                print(f"  {dept_name} {course_name} {section_name}: {len(books)} book(s)")

                driver.back()
                human_pause(2, 4)
                check_for_bot_block(driver)

    print("\nScraping complete.")

    if not all_textbooks:
        print("No textbook data collected.")
        return

    df = pd.DataFrame(all_textbooks)
    term_label = selected_term_text.replace(" ", "_")
    output_file = f"bookstore_textbooks_{term_label}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Saved {len(all_textbooks)} rows to: {output_file}")


# ── Click the search/submit button ───────────────────────────────────────────

def click_search_button(driver):
    """
    Tries several CSS selectors to find and click the 'Find Materials' button.
    Returns True if clicked, False if not found.
    """
    selectors = [
        "button.search-enter-button",
        "button[class*='search-enter']",
        "input[type='submit']",
        "button[type='submit']",
        "button[class*='find']",
        "button[class*='submit']",
        "[class*='textbooks-search'] button",
    ]
    for sel in selectors:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, sel)
            btn.click()
            return True
        except NoSuchElementException:
            continue
    return False


# ── One-time diagnostics ──────────────────────────────────────────────────────

def diagnose_buttons(driver):
    """Prints all buttons on the page to help identify the search button."""
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\n[DIAGNOSTIC] {len(buttons)} button(s) on page:")
    for b in buttons:
        print(f"  text='{b.text[:50]}' id='{b.get_attribute('id')}' class='{b.get_attribute('class')[:80]}'")


def diagnose_results(driver):
    """Prints page structure to help identify how book results are wrapped."""
    print("\n[DIAGNOSTIC] Looking for book/material elements on results page...")
    for keyword in ["book", "material", "textbook", "result", "course-list"]:
        matches = driver.find_elements(By.CSS_SELECTOR, f"[class*='{keyword}']")
        if matches:
            print(f"\n  class*='{keyword}': {len(matches)} element(s)")
            for el in matches[:3]:
                print(f"    <{el.tag_name}> class='{el.get_attribute('class')[:80]}'")
                print(f"    text preview: '{el.text[:120]}'")


# ── Scrape results for one section ───────────────────────────────────────────

def scrape_results(driver, term, dept, course, section):
    """Scrapes textbook data from the results page for one course section."""
    books = []
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                "[class*='book'], [class*='material'], [class*='textbook']"))
        )
    except TimeoutException:
        return books

    book_elements = driver.find_elements(By.CSS_SELECTOR,
        "[class*='book-detail'], [class*='materialItem'], [class*='bookInfo'], "
        "[class*='book-info'], [class*='course-list-item']")

    for el in book_elements:
        data = {
            "Term":                    term,
            "Department":              dept,
            "Course":                  course,
            "Section":                 section,
            "Title":                   extract_text(el, "[class*='title'], h1, h2, h3"),
            "Author":                  extract_text(el, "[class*='author']"),
            "ISBN":                    extract_text(el, "[class*='isbn']"),
            "Edition":                 extract_text(el, "[class*='edition']"),
            "Publisher":               extract_text(el, "[class*='publisher']"),
            "Required_or_Recommended": extract_text(el, "[class*='required'], [class*='recommended']"),
            "New_Price":               extract_text(el, "[class*='newPrice'], [class*='price-new']"),
            "Used_Price":              extract_text(el, "[class*='usedPrice'], [class*='price-used']"),
        }
        if data["Title"] or data["ISBN"]:
            books.append(data)

    return books


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    scrape_bookstore()
