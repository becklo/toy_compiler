import subprocess
import os

def main():
    input_path = os.path.join(os.path.dirname(__file__), 'input')
    expected_output_path = os.path.join(os.path.dirname(__file__), 'expected_output')
    for filename in os.listdir(input_path):
        input_file = os.path.join(input_path, filename)
        print(input_file)
        result = subprocess.getoutput(f'cat {input_file} | poetry run parser')
        print(result)
        expected_output_file = os.path.join(expected_output_path, filename)
        with open(expected_output_file, 'r') as f:
            expected_output = f.read()
        assert result == expected_output

if __name__ == '__main__':
    main()