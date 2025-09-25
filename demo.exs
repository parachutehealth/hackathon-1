#!/usr/bin/env elixir

# Demonstration script showing how to use the FhirElixir library
# This is equivalent to the Ruby example in the README:
#   xml = File.read('patient-example.xml')
#   patient = FHIR.from_contents(xml)
#   puts patient.to_xml

Mix.install([
  {:sweet_xml, "~> 0.7"}
])

# Load the library modules
Code.require_file("lib/fhir_elixir.ex")
Code.require_file("lib/fhir_elixir/resource.ex")

# Read the patient example XML file
xml = File.read!("patient-example.xml")

# Parse the FHIR content
patient = FhirElixir.from_contents(xml)

# Print the parsed patient information
IO.puts("=== Parsed Patient Information ===")
IO.puts("Resource Type: #{patient.resource_type}")
IO.puts("ID: #{patient.parsed_data.id}")
IO.puts("Active: #{patient.parsed_data.active}")
IO.puts("Gender: #{patient.parsed_data.gender}")
IO.puts("Birth Date: #{patient.parsed_data.birth_date}")

# Print names
IO.puts("\nNames:")
for name <- patient.parsed_data.name do
  given_names = Enum.join(name.given, " ")
  IO.puts("  #{name.use}: #{given_names} #{name.family}")
end

# Print contact information
IO.puts("\nContact Information:")
for telecom <- patient.parsed_data.telecom do
  IO.puts("  #{telecom.system} (#{telecom.use}): #{telecom.value}")
end

# Print addresses
IO.puts("\nAddresses:")
for address <- patient.parsed_data.address do
  lines = Enum.join(address.line, ", ")
  IO.puts("  #{address.use}: #{lines}, #{address.city}, #{address.state} #{address.postal_code}, #{address.country}")
end

# Convert back to XML and print
IO.puts("\n=== Generated XML ===")
IO.puts(FhirElixir.Resource.to_xml(patient))

IO.puts("\n=== Demonstration Complete ===")
IO.puts("Usage: elixir demo.exs")