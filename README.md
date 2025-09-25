# FhirElixir

An Elixir library for parsing and generating FHIR (Fast Healthcare Interoperability Resources) data.

## Features

- Parse FHIR resources from XML content
- Generate XML output from parsed FHIR resources
- Support for Patient and Observation resource types
- Extensible architecture for additional FHIR resource types
- Comprehensive error handling

## Installation

Add `fhir_elixir` to your list of dependencies in `mix.exs`:

```elixir
def deps do
  [
    {:fhir_elixir, "~> 0.1.0"},
    {:sweet_xml, "~> 0.7"}
  ]
end
```

## Usage

### Basic Example

```elixir
# Read FHIR XML content
xml = File.read!("patient-example.xml")

# Parse the FHIR content
patient = FhirElixir.from_contents(xml)

# Generate XML output
IO.puts(FhirElixir.Resource.to_xml(patient))
```

### API Reference

#### `FhirElixir.from_contents/1`

Parse FHIR content from XML string:

```elixir
xml = "<Patient><id value='123'/></Patient>"
resource = FhirElixir.from_contents(xml)
```

#### `FhirElixir.from_file/1`

Parse FHIR content from file:

```elixir
patient = FhirElixir.from_file("patient-example.xml")
```

#### `FhirElixir.Resource.to_xml/1`

Convert parsed FHIR resource back to XML:

```elixir
xml_output = FhirElixir.Resource.to_xml(patient)
```

### Supported Resource Types

- **Patient**: Demographics and administrative information
- **Observation**: Clinical measurements and assessments
- **Generic**: Basic support for other FHIR resource types

### Example Output

```elixir
patient = FhirElixir.from_contents(xml)

# Access parsed data
patient.resource_type          # "Patient"
patient.parsed_data.id         # "example"
patient.parsed_data.gender     # "male"
patient.parsed_data.name       # List of name structures
```

## Development

Run the demonstration:

```bash
elixir demo.exs
```

Run tests:

```bash
mix test
```

## Examples to Reference

- [FHIR Models (Ruby)](https://github.com/inferno-framework/fhir_models)
- [Implementing FHIR with Ruby on Rails](https://idyllic.co/implementing-fhir-with-ruby-on-rails/)

## Ruby Equivalent

This library provides equivalent functionality to:

```ruby
xml = File.read('patient-example.xml')
patient = FHIR.from_contents(xml)
puts patient.to_xml
```