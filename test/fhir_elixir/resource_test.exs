defmodule FhirElixir.ResourceTest do
  use ExUnit.Case
  alias FhirElixir.Resource

  describe "to_xml/1" do
    test "generates Patient XML correctly" do
      patient_data = %{
        id: "123",
        active: "true",
        name: [
          %{use: "official", family: "Doe", given: ["John", "James"]},
          %{use: "usual", family: "", given: ["Johnny"]}
        ],
        telecom: [
          %{system: "phone", value: "555-1234", use: "home"},
          %{system: "email", value: "john@example.com", use: "work"}
        ],
        gender: "male",
        birth_date: "1980-01-01",
        address: [
          %{
            use: "home",
            type: "both",
            line: ["123 Main St", "Apt 4B"],
            city: "Anytown",
            state: "NY",
            postal_code: "12345",
            country: "USA"
          }
        ]
      }

      resource = %Resource{
        resource_type: "Patient",
        raw_xml: "",
        parsed_data: patient_data
      }

      xml = Resource.to_xml(resource)

      assert String.contains?(xml, "<Patient xmlns=\"http://hl7.org/fhir\">")
      assert String.contains?(xml, "<id value=\"123\"/>")
      assert String.contains?(xml, "<active value=\"true\"/>")
      assert String.contains?(xml, "<gender value=\"male\"/>")
      assert String.contains?(xml, "<birthDate value=\"1980-01-01\"/>")
      assert String.contains?(xml, "<family value=\"Doe\"/>")
      assert String.contains?(xml, "<given value=\"John\"/>")
      assert String.contains?(xml, "<given value=\"James\"/>")
      assert String.contains?(xml, "telecom system=\"phone\" value=\"555-1234\" use=\"home\"")
      assert String.contains?(xml, "<city value=\"Anytown\"/>")
    end

    test "generates Observation XML correctly" do
      observation_data = %{
        id: "obs-123",
        status: "final",
        code: %{
          coding: [
            %{system: "http://loinc.org", code: "15074-8", display: "Glucose"}
          ],
          text: "Blood Glucose"
        },
        subject: %{reference: "Patient/123", display: "John Doe"},
        value: %{value: "95", unit: "mg/dL", system: "http://unitsofmeasure.org", code: "mg/dL"}
      }

      resource = %Resource{
        resource_type: "Observation",
        raw_xml: "",
        parsed_data: observation_data
      }

      xml = Resource.to_xml(resource)

      assert String.contains?(xml, "<Observation xmlns=\"http://hl7.org/fhir\">")
      assert String.contains?(xml, "<id value=\"obs-123\"/>")
      assert String.contains?(xml, "<status value=\"final\"/>")
      assert String.contains?(xml, "<coding system=\"http://loinc.org\" code=\"15074-8\" display=\"Glucose\"/>")
      assert String.contains?(xml, "<text value=\"Blood Glucose\"/>")
      assert String.contains?(xml, "<subject reference=\"Patient/123\">")
      assert String.contains?(xml, "<display value=\"John Doe\"/>")
      assert String.contains?(xml, "<valueQuantity value=\"95\" unit=\"mg/dL\"")
    end

    test "handles empty or nil values gracefully" do
      minimal_data = %{
        id: "",
        active: nil,
        name: [],
        telecom: nil,
        gender: "",
        birth_date: nil,
        address: []
      }

      resource = %Resource{
        resource_type: "Patient",
        raw_xml: "",
        parsed_data: minimal_data
      }

      xml = Resource.to_xml(resource)

      assert String.contains?(xml, "<Patient xmlns=\"http://hl7.org/fhir\">")
      refute String.contains?(xml, "<id")
      refute String.contains?(xml, "<active")
      refute String.contains?(xml, "<name")
      refute String.contains?(xml, "<gender")
      refute String.contains?(xml, "<birthDate")
    end
  end
end