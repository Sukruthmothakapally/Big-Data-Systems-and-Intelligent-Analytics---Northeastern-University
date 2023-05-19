# Great Expectations

> [Great Expectations](https://greatexpectations.io/) is the leading tool for validating, documenting, and profiling your data to maintain quality and improve communication between teams. It acts as an unit test for data.

# Features

-   **Automated data profiling** <br>
    The library profiles your data to get basic statistics, and automatically generates a suite of Expectations based on what is observed in the data.
-   **Data validation** <br>
    Expectation Suite passes or fails, and returns any unexpected values that failed a test
-   **Data Docs** <br>
    Renders HTML file of Expectations in clean, human-readable documentation containing both Expectation Suites and data Validation Results
-   **Diverse Datasources and Store backends** <br>
    Various datasources such Pandas dataframes, Spark dataframes, and SQL databases via SQLAlchemy.

## Dataset

-   [FAA_Registration.csv]

---

## Tutorial

1. Create a python environment and activate it

```bash
python -m venv venv
source venv/bin/activate
```

2. Install module `great_expectations`

```bash
pip install great_expectations==0.15.46
```

3. Verify the version

```bash
python --version
# Python 3.9.13

great_expectations --version
# great_expectations, version 0.15.46
```

4. Initialize at the base dir

```bash
great_expectations init
```

Confirm the prompt

5. Download the dataset
   Place the dataset in the data dir

6. Launch cli datasource process

```bash
great_expectations datasource new
```

# Input following in the prompt

# > `1` - Local File<br> `1` - Pandas <br> `../data` - relative path to datasets

This open a Jupyter notebook, <br>

-   Change to `datasource_name` var to `faa_registration`
    ```
    datasource_name = "fAA_Registration"
    ```
-   Run all th cells
-   Close Jupyter notebook
-   Wait for terminal to show `Saving file at /datasource_new.ipynb`

7. Create Expectations suite for faa_registration datasets

```bash
great_expectations suite new
```

Input following in the prompt

> `3` - Automatically, using a profiler <br> `1` - Select index of file `fAA_Registration.csv` <br> `faa_registration_suite` - suite name

This open a Jupyter notebook, <br>

-   To exclude any column Update `exclude_column_names`
    ```python
    exclude_column_names = [
        "N-NUMBER",
        "SERIAL NUMBER",
        "MFR MDL CODE",
        "ENG MFR MDL",
    #    "YEAR MFR",
        "TYPE REGISTRANT",
        "NAME",
        "STREET",
        "STREET2",
        "CITY",
        "STATE",
        "ZIP CODE",
        "REGION",
        "COUNTY",
        "COUNTRY",
    #    "LAST ACTION DATE",
    #    "CERT ISSUE DATE",
        "CERTIFICATION",
        "TYPE AIRCRAFT",
        "TYPE ENGINE",
        "STATUS CODE",
        "MODE S CODE",
        "FRACT OWNER",
        "AIR WORTH DATE",
        "OTHER NAMES(1)",
        "OTHER NAMES(2)",
        "OTHER NAMES(3)",
        "OTHER NAMES(4)",
        "OTHER NAMES(5)",
    #    "EXPIRATION DATE",
    #    "UNIQUE ID",
        "KIT MFR",
        "KIT MODEL",
        "MODE S CODE HEX",
        "X35",
    ]
    ```
-   Run to create default expectation and analyze the result
-   Wait for terminal to show `Saving file at /*.ipynb`
-   Modify expectation as per need <br>
    Modified the JSON file `great_expectations/expectations/fAA_Registration_suite.json` and kept necessary expectations <br>

8. Create checkpoint

```bash
great_expectations checkpoint new fAA_Registration_v1
```

This open a Jupyter notebook, <br>

-   Run all cells.
-   Open report in new page

9. Export the requirements and Commit changes to github
