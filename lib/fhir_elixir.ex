defmodule FhirElixir do
  @moduledoc """
  FhirElixir - A library for parsing and generating FHIR (Fast Healthcare Interoperability Resources) data.

  This library provides functionality similar to the Ruby FHIR library, allowing you to:
  - Parse FHIR resources from XML content
  - Generate XML output from FHIR resources

  ## Examples

      xml = File.read!("patient-example.xml")
      patient = FhirElixir.from_contents(xml)
      IO.puts(patient.to_xml)

  """

  import SweetXml

  @doc """
  Parse FHIR content from XML string and return a FHIR resource.

  ## Examples

      iex> xml = "<Patient><id value='123'/></Patient>"
      iex> patient = FhirElixir.from_contents(xml)
      iex> patient.resource_type
      "Patient"

  """
  def from_contents(xml_content) when is_binary(xml_content) do
    try do
      parsed = xml_content |> parse()
      resource_type = parsed |> xpath(~x"name(/*)"s)

      %FhirElixir.Resource{
        resource_type: resource_type,
        raw_xml: xml_content,
        parsed_data: extract_resource_data(parsed, resource_type)
      }
    rescue
      error ->
        {:error, "Failed to parse XML: #{inspect(error)}"}
    end
  end

  @doc """
  Parse FHIR content from a file path.

  ## Examples

      patient = FhirElixir.from_file("patient-example.xml")

  """
  def from_file(file_path) do
    case File.read(file_path) do
      {:ok, content} -> from_contents(content)
      {:error, reason} -> {:error, "Failed to read file: #{reason}"}
    end
  end

  # Extract resource data based on resource type
  defp extract_resource_data(parsed_xml, resource_type) do
    case resource_type do
      "Patient" -> extract_patient_data(parsed_xml)
      "Observation" -> extract_observation_data(parsed_xml)
      _ -> extract_generic_data(parsed_xml)
    end
  end

  # Extract Patient-specific data
  defp extract_patient_data(parsed_xml) do
    %{
      id: parsed_xml |> xpath(~x"//id/@value"s),
      active: parsed_xml |> xpath(~x"//active/@value"s),
      name: extract_human_names(parsed_xml),
      telecom: extract_contact_points(parsed_xml),
      gender: parsed_xml |> xpath(~x"//gender/@value"s),
      birth_date: parsed_xml |> xpath(~x"//birthDate/@value"s),
      address: extract_addresses(parsed_xml)
    }
  end

  # Extract Observation-specific data
  defp extract_observation_data(parsed_xml) do
    %{
      id: parsed_xml |> xpath(~x"//id/@value"s),
      status: parsed_xml |> xpath(~x"//status/@value"s),
      code: extract_codeable_concept(parsed_xml, "//code"),
      subject: extract_reference(parsed_xml, "//subject"),
      value: extract_value(parsed_xml)
    }
  end

  # Extract generic resource data
  defp extract_generic_data(parsed_xml) do
    %{
      id: parsed_xml |> xpath(~x"//id/@value"s)
    }
  end

  # Helper functions for extracting complex data types
  defp extract_human_names(parsed_xml) do
    parsed_xml
    |> xpath(~x"//name"l)
    |> Enum.map(fn name ->
      %{
        use: name |> xpath(~x"./@use"s),
        family: name |> xpath(~x"./family/@value"s),
        given: name |> xpath(~x"./given/@value"ls)
      }
    end)
  end

  defp extract_contact_points(parsed_xml) do
    parsed_xml
    |> xpath(~x"//telecom"l)
    |> Enum.map(fn telecom ->
      %{
        system: telecom |> xpath(~x"./@system"s),
        value: telecom |> xpath(~x"./@value"s),
        use: telecom |> xpath(~x"./@use"s)
      }
    end)
  end

  defp extract_addresses(parsed_xml) do
    parsed_xml
    |> xpath(~x"//address"l)
    |> Enum.map(fn address ->
      %{
        use: address |> xpath(~x"./@use"s),
        type: address |> xpath(~x"./@type"s),
        line: address |> xpath(~x"./line/@value"ls),
        city: address |> xpath(~x"./city/@value"s),
        state: address |> xpath(~x"./state/@value"s),
        postal_code: address |> xpath(~x"./postalCode/@value"s),
        country: address |> xpath(~x"./country/@value"s)
      }
    end)
  end

  defp extract_codeable_concept(parsed_xml, xpath_expr) do
    concept = parsed_xml |> xpath(~x"#{xpath_expr}")
    if concept do
      %{
        coding: concept |> xpath(~x"./coding"l) |> Enum.map(fn coding ->
          %{
            system: coding |> xpath(~x"./@system"s),
            code: coding |> xpath(~x"./@code"s),
            display: coding |> xpath(~x"./@display"s)
          }
        end),
        text: concept |> xpath(~x"./text/@value"s)
      }
    end
  end

  defp extract_reference(parsed_xml, xpath_expr) do
    ref = parsed_xml |> xpath(~x"#{xpath_expr}")
    if ref do
      %{
        reference: ref |> xpath(~x"./@reference"s),
        display: ref |> xpath(~x"./display/@value"s)
      }
    end
  end

  defp extract_value(parsed_xml) do
    cond do
      quantity = parsed_xml |> xpath(~x"//valueQuantity") ->
        %{
          value: quantity |> xpath(~x"./@value"s),
          unit: quantity |> xpath(~x"./@unit"s),
          system: quantity |> xpath(~x"./@system"s),
          code: quantity |> xpath(~x"./@code"s)
        }

      string_value = parsed_xml |> xpath(~x"//valueString/@value"s) ->
        %{value: string_value}

      true ->
        nil
    end
  end
end