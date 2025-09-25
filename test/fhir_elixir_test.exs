defmodule FhirElixirTest do
  use ExUnit.Case
  doctest FhirElixir

  describe "from_contents/1" do
    test "parses Patient XML correctly" do
      xml = """
      <Patient xmlns="http://hl7.org/fhir">
        <id value="123"/>
        <active value="true"/>
        <name use="official">
          <family value="Doe"/>
          <given value="John"/>
        </name>
        <gender value="male"/>
        <birthDate value="1980-01-01"/>
      </Patient>
      """

      patient = FhirElixir.from_contents(xml)

      assert patient.resource_type == "Patient"
      assert patient.parsed_data.id == "123"
      assert patient.parsed_data.active == "true"
      assert patient.parsed_data.gender == "male"
      assert patient.parsed_data.birth_date == "1980-01-01"

      assert length(patient.parsed_data.name) == 1
      name = List.first(patient.parsed_data.name)
      assert name.use == "official"
      assert name.family == "Doe"
      assert name.given == ["John"]
    end

    test "parses Observation XML correctly" do
      xml = """
      <Observation xmlns="http://hl7.org/fhir">
        <id value="obs-123"/>
        <status value="final"/>
        <code>
          <coding system="http://loinc.org" code="15074-8" display="Glucose"/>
        </code>
        <subject reference="Patient/123"/>
        <valueQuantity value="95" unit="mg/dL"/>
      </Observation>
      """

      observation = FhirElixir.from_contents(xml)

      assert observation.resource_type == "Observation"
      assert observation.parsed_data.id == "obs-123"
      assert observation.parsed_data.status == "final"
      assert observation.parsed_data.subject.reference == "Patient/123"
      assert observation.parsed_data.value.value == "95"
      assert observation.parsed_data.value.unit == "mg/dL"
    end

    test "handles invalid XML gracefully" do
      invalid_xml = "<Invalid><unclosed>"

      result = FhirElixir.from_contents(invalid_xml)

      assert {:error, error_message} = result
      assert String.contains?(error_message, "Failed to parse XML")
    end
  end

  describe "from_file/1" do
    test "reads and parses patient example file" do
      patient = FhirElixir.from_file("patient-example.xml")

      assert patient.resource_type == "Patient"
      assert patient.parsed_data.id == "example"
      assert patient.parsed_data.active == "true"
      assert patient.parsed_data.gender == "male"
      assert patient.parsed_data.birth_date == "1974-12-25"

      # Check names
      assert length(patient.parsed_data.name) == 2
      official_name = Enum.find(patient.parsed_data.name, &(&1.use == "official"))
      assert official_name.family == "Chalmers"
      assert official_name.given == ["Peter", "James"]

      # Check telecom
      assert length(patient.parsed_data.telecom) == 2
      phone = Enum.find(patient.parsed_data.telecom, &(&1.system == "phone"))
      assert phone.value == "(03) 5555 6473"
      assert phone.use == "work"

      # Check address
      assert length(patient.parsed_data.address) == 1
      address = List.first(patient.parsed_data.address)
      assert address.use == "home"
      assert address.city == "PleasantVille"
      assert address.country == "Australia"
    end

    test "handles non-existent file" do
      result = FhirElixir.from_file("non-existent.xml")

      assert {:error, error_message} = result
      assert String.contains?(error_message, "Failed to read file")
    end
  end
end