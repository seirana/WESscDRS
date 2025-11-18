#!/usr/bin/env python3

import pandas as pd

def main():
    # Hard-coded test paths
    input_path = "/home/shashemi/Desktop/Projects/scDRS/ForGithub/input_test.csv"
    output_path = "/home/shashemi/Desktop/Projects/scDRS/ForGithub/output_test.csv"

    print("Reading:", input_path)
    df = pd.read_csv(input_path)

    # Multiply column 0 by 5
    first_col_name = df.columns[0]
    df[first_col_name] = df[first_col_name] * 5

    print("Writing:", output_path)
    df.to_csv(output_path, index=False)

    print("Finished successfully.")

if __name__ == "__main__":
    main()

