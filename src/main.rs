use std::collections::HashMap;
use std::env;
use std::error::Error;
use std::fs::File;
use std::io::{prelude::*, BufReader};
use std::time::Instant;

extern crate getopts;
extern crate glob;
use getopts::Options;
use glob::glob;
use serde_json::Value;

#[derive(Debug)]
struct Status {
    time: f32,
    lines: u32,
    empty_keys: u32,
    empty_items: u32,
    duplicate_keys: u32,
    invalid_items: u32,
    // key_func_err: u32,
    // validation_err: u32,
}

impl Default for Status {
    fn default() -> Status {
        Status {
            time: 0.0,
            lines: 0,
            empty_keys: 0,
            empty_items: 0,
            duplicate_keys: 0,
            invalid_items: 0,
        }
    }
}

fn is_valid(itm: &Value) -> bool {
    if !itm.is_object() {
        return false
    }
    let obj = itm.as_object().unwrap();
    if obj.len() < 3 || obj.len() > 6 {
        return false
    }
    if itm.get("source").unwrap().as_str() == Some("") {
        return false
    }
    let has_author = itm.get("author").unwrap().as_str().unwrap().len() > 1;
    let has_txt = itm.get("text").unwrap().as_str().unwrap().len() > 3;
    has_txt && has_author
}

fn key_func(itm: &Value) -> String {
    let mut k = String::new();
    let author = itm.get("author").unwrap().as_str().unwrap();
    k.push_str(&author.to_ascii_lowercase());
    let text = itm.get("text").unwrap().as_str().unwrap();
    k.push_str(&text.to_ascii_lowercase().replace(" ", ""));
    k
}

fn load_jl_file(path: &str) -> Result<(), Box<dyn Error>> {
    let tstart = Instant::now();

    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut db: HashMap<String, _> = HashMap::new();
    let mut stat = Status {
        ..Default::default()
    };

    for line in reader.lines() {
        let l = line?;
        if l.trim() == "" {
            continue;
        }

        // Increment non-empty lines
        stat.lines += 1;

        let itm: Value = serde_json::from_str(&l)?;

        // Ignore null items, they don't make sense
        if itm.is_object() && itm.as_object().unwrap().len() == 0 {
            stat.empty_items += 1;
            continue;
        } else if itm.is_array() && itm.as_array().unwrap().len() == 0 {
            stat.empty_items += 1;
            continue;
        } else if itm.is_null() || itm.is_boolean() {
            // INVALID TYPE
            continue;
        }

        if !is_valid(&itm) {
            stat.invalid_items += 1;
            continue;
        }

        let key = key_func(&itm);
        // Ignore null keys, they don't make sense
        if key == "" {
            stat.empty_keys += 1;
            continue;
        }

        if db.contains_key(&key) {
            stat.duplicate_keys += 1;
        }

        // Overwrite key, if exists
        db.insert(key, itm);
    }

    stat.time = tstart.elapsed().as_millis() as f32;

    println!("{:?}", stat);
    println!("{:?} entries", db.len());

    Ok(())
}

// This is the main function
fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = env::args().collect();
    // let program = args[0].clone();

    let mut opts = Options::new();
    opts.optflag("h", "help", "print this help menu");
    opts.reqopt("i", "", "set input file", "NAME");

    let matches = match opts.parse(&args[1..]) {
        Ok(m) => m,
        Err(e) => panic!(e.to_string()),
    };
    println!("ARGS: {:?}", matches);

    if matches.opt_present("h") {
        print!("Help text");
        return Ok(());
    }

    let tstart = Instant::now();

    let input = matches.opt_str("i").unwrap();
    for entry in glob(input.as_str()).expect("Failed to read glob pattern") {
        match entry {
            Ok(path) => {
                println!("Loading: {:?}", path.display());
                load_jl_file(path.to_str().unwrap());
            },
            Err(e) => println!("{:?}", e),
        }
    }

    let elapsed = tstart.elapsed().as_millis();
    println!("Elapsed time: {:?} ms", elapsed);

    Ok(())
}
