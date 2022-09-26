use pyo3::exceptions::PyException;
use pyo3::{prelude::*, create_exception, PyResult};
use inferno::flamegraph::Options;
use inferno::flamegraph::from_lines as inferno_from_lines;
use inferno::flamegraph::Palette;
create_exception!(pyinferno, InfernoError, PyException);

#[pyfunction]
fn flamegraph_from_lines(lines: Vec<&str>, title: Option<String>) -> PyResult<String> {
    let colors = Palette::Multi(inferno::flamegraph::color::MultiPalette::Python);
    let mut opts = Options::default();
    opts.colors = colors;
    if let Some(s) = title {
        opts.title = s
    }

    let mut buf: Vec<u8> = Vec::new();
    inferno_from_lines(&mut opts, lines, &mut buf).map_err(|e| InfernoError::new_err(e.to_string()))?;
    let string = String::from_utf8(buf)?;
    Ok(string)
}

/// A Python module implemented in Rust.
#[pymodule]
fn pyinferno(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(flamegraph_from_lines, m)?)?;
    m.add("InfernoError", _py.get_type::<InfernoError>())?;
    Ok(())
}
