import os
from datetime import timedelta
from pathlib import Path

from core.helpers import (
    HelpersException,
    as_jsonl,
    as_row,
    classname,
    create_text_file,
    erase_directory_contents,
    get_container,
    get_directory,
    get_environment_variable,
    get_resource,
    get_resource_with_timestamp,
    get_timestamp,
    i,
    measure_execution_time,
    read_json,
    read_json_lines,
    read_text,
    read_text_file,
    read_text_lines,
    remove_directory,
    write_json,
    write_text,
    write_text_lines,
)


def test_classname():
    assert classname(1) == "int"
    assert classname("str") == "str"


def test_i():
    assert i(2) == "        "  # 2 times indentation
    assert i(0) == ""


def test_get_timestamp():
    ts = get_timestamp(offset=timedelta(0))
    assert len(ts) == 14
    assert ts.isdigit()


def test_helpers_exception():
    e = HelpersException("test_id", "test message")
    assert str(e) == "test_id: test message"


def test_file_operations(tmp_path: Path):
    res = tmp_path / "test.txt"
    with create_text_file(res) as f:
        f.write("hello")

    assert res.exists()
    assert read_text(res) == "hello"

    with read_text_file(res) as f:
        assert f.read() == "hello"

    write_text(res, "world")
    assert read_text(res) == "world"


def test_json_operations(tmp_path: Path):
    res = tmp_path / "test.json"
    data = {"key": "value"}
    write_json(res, data)
    assert read_json(res) == data


def test_lines_operations(tmp_path: Path):
    res = tmp_path / "test.txt"
    lines = ["a", "b", "c"]
    
    def gen():
        yield from lines
        
    write_text_lines(res, gen)
    read_lines = list(read_text_lines(res))
    assert read_lines == lines


def test_jsonl_operations(tmp_path: Path):
    res = tmp_path / "test.jsonl"
    rows = [{"a": "1"}, {"b": "2"}]
    with create_text_file(res) as f:
        for row in rows:
            f.write(as_jsonl(row))
            
    read_rows = list(read_json_lines(res))
    assert read_rows == rows
    assert as_row('{"c": 3}') == {"c": 3}


def test_directory_operations(tmp_path: Path):
    d = get_directory(tmp_path / "dir")
    assert d.exists()
    assert d.is_dir()
    
    c = get_container(d, "sub")
    assert c.exists()
    assert c.parent == d
    
    res = get_resource(c, "file", ".txt")
    assert res.name == "file.txt"
    assert res.parent == c
    
    res_ts = get_resource_with_timestamp(c, "file", ".txt")
    assert res_ts.parent == c
    assert res_ts.suffix == ".txt"
    assert res_ts.name.startswith("file_")
    
    # erase
    (d / "test.txt").touch()
    (d / "sub2").mkdir()
    (d / "sub2" / "test2.txt").touch()
    erase_directory_contents(d)
    assert d.exists()
    assert not list(d.iterdir())
    
    remove_directory(d)
    assert not d.exists()


def test_get_environment_variable():
    os.environ["TEST_ENV_VAR"] = "val"
    assert get_environment_variable("TEST_ENV_VAR") == "val"
    assert get_environment_variable("NON_EXISTENT", "default") == "default"


def test_measure_execution_time():
    def task():
        return 42
    result, time_taken = measure_execution_time(task)
    assert result == 42
    assert isinstance(time_taken, float)
