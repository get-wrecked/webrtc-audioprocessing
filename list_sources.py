import subprocess
import json
import os

def gn_desc(out_dir, target, attribute):
    """Run the 'gn desc' command for a specific attribute within the src folder."""
    original_cwd = os.getcwd()  # Save current directory
    os.chdir('src')  # Change to src directory

    command = ['gn', 'desc', out_dir, target, attribute, '--format=json']
    result = subprocess.run(command, capture_output=True, text=True)
    os.chdir(original_cwd)  # Restore original working directory

    if result.returncode != 0:
        raise Exception(f"GN desc failed: {result.stderr}")
    return json.loads(result.stdout)

def collect_files(out_dir, target, visited=None):
    """Recursively collect both source and header files for a target."""
    if visited is None:
        visited = set()

    if target in visited:
        return set(), set()
    visited.add(target)

    source_files = set()
    header_files = set()

    data = gn_desc(out_dir, target, "sources")
    print(target)
    files = set(data.get(target, {}).get("sources", []))
    for file in files:
        if file.endswith(('.c', '.cc', '.cpp')):
            source_files.add(file)
        elif file.endswith(('.h', '.hh', '.hpp')):
            header_files.add(file)

    deps_data = gn_desc(out_dir, target, "deps")
    for dep in deps_data.get(target, {}).get("deps", []):
        if dep.startswith("//"):
            dep_sources, dep_headers = collect_files(out_dir, dep, visited)
            source_files.update(dep_sources)
            header_files.update(dep_headers)

    return source_files, header_files

def save_to_cmake_file(files, filename, var_name):
    """Save the collected files to a CMake file in a set format."""
    sorted_files = sorted([f.replace('//', 'src/') for f in files])
    with open(filename, 'w') as file:
        file.write(f"set({var_name}\n")
        for file_path in sorted_files:
            file.write(f"    {file_path}\n")
        file.write(")\n")

def main():
    out_dir = 'out/Default'  # Change this to your GN output directory
    target = '//modules/audio_processing:audio_processing'  # Change this to your specific target

    try:
        source_files, header_files = collect_files(out_dir, target)

        save_to_cmake_file(source_files, "sources_new.cmake", "SOURCE_FILES")
        # Listing header by this method is not foolproof. It misses some headers. Using alternative method in CMakeLists.txt
        # save_to_cmake_file(header_files, "headers_new.cmake", "HEADER_FILES")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
