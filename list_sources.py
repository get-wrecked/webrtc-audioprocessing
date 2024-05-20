import subprocess
import json

def gn_desc(out_dir, target, attribute):
    """Run the 'gn desc' command for a specific attribute."""
    command = ['gn', 'desc', out_dir, target, attribute, '--format=json']
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"GN desc failed: {result.stderr}")
    return json.loads(result.stdout)

def collect_sources(out_dir, target, collected=None, visited=None):
    """Recursively collect all source files for a target."""
    if collected is None:
        collected = set()
    if visited is None:
        visited = set()

    if target in visited:
        return collected
    visited.add(target)

    # Get the direct sources of the target
    data = gn_desc(out_dir, target, "sources")
    print (target)
    sources = set(data.get(target, {}).get("sources", []))
    for source in sources:
        if source.endswith(('.c', '.cc', '.cpp')):
            collected.add(source)

    # Recursively collect sources from dependencies
    deps_data = gn_desc(out_dir, target, "deps")
    for dep in deps_data.get(target, {}).get("deps", []):
        # Filter out system and external libraries
        if dep.startswith("//"):
            collect_sources(out_dir, dep, collected, visited)

    return collected

def main():
    out_dir = 'out/mac_arm64'  # Change this to your GN output directory
    target = '//modules/audio_processing:residual_echo_detector'  # Change this to your specific target

    try:
        sources = collect_sources(out_dir, target)
        sources = [src.replace('//', 'src/') for src in sorted(sources)]
        for source in sorted(sources):
            print(source)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
