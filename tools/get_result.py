"""
save_result(estimate_kmps, file_path) - saves the results in file

Parametars:
estimate_kmps - km/s
file_path - name of the file with result

Result:
None
"""

def save_result(estimate_kmps, file_path):
    # Format the estimate_kmps to have a precision
    # of 5 significant figures
    estimate_kmps_formatted = f'{estimate_kmps:.4f}'
    
    # Create a string to write to the file
    output_string = estimate_kmps_formatted

    # Write to the file
    with open(file_path, 'w') as file:
        file.write(output_string)
    
def main():
    # TODO: Replace with your estimate
    estimate_kmps = 7.1234367890123415
    file_path = 'result.txt'    # Replace with your desired file path 

    save_result(estimate_kmps, file_path)  
    print('Result is written to', file_path)

    
main()
