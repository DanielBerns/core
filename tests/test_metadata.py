from pathlib import Path

from core.metadata import Metadata


def test_metadata_operations(tmp_path: Path):
    m = Metadata(tmp_path)
    
    # Metadata file doesn't exist yet, should not crash
    m.read()
    assert m.table == {}
    
    # Add values
    m.add("key1", "value1")
    m.add("key2", 42)
    assert m.table == {"key1": "value1", "key2": 42}
    
    # Write to file
    m.write()
    
    # Check that file exists
    assert m.resource.exists()
    assert m.resource.name == "metadata.json"
    
    # Read from file into new instance
    m2 = Metadata(tmp_path)
    m2.read()
    assert m2.table == {"key1": "value1", "key2": 42}
