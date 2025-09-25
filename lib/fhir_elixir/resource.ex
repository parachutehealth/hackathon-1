defmodule FhirElixir.Resource do
  @moduledoc """
  Represents a FHIR resource with the ability to convert back to XML.
  """

  defstruct [:resource_type, :raw_xml, :parsed_data]

  @doc """
  Convert the FHIR resource back to XML string.

  ## Examples

      patient = FhirElixir.from_contents(xml)
      xml_output = patient.to_xml()

  """
  def to_xml(%__MODULE__{raw_xml: _raw_xml, parsed_data: parsed_data, resource_type: resource_type}) do
    generate_xml(resource_type, parsed_data)
  end

  # Generate XML for different resource types
  defp generate_xml("Patient", data) do
    """
    <Patient xmlns="http://hl7.org/fhir">
    #{generate_id(data.id)}
    #{generate_active(data.active)}
    #{generate_names(data.name)}
    #{generate_telecoms(data.telecom)}
    #{generate_gender(data.gender)}
    #{generate_birth_date(data.birth_date)}
    #{generate_addresses(data.address)}
    </Patient>
    """
    |> String.trim()
  end

  defp generate_xml("Observation", data) do
    """
    <Observation xmlns="http://hl7.org/fhir">
    #{generate_id(data.id)}
    #{generate_status(data.status)}
    #{generate_code(data.code)}
    #{generate_subject_reference(data.subject)}
    #{generate_value(data.value)}
    </Observation>
    """
    |> String.trim()
  end

  defp generate_xml(resource_type, data) do
    """
    <#{resource_type} xmlns="http://hl7.org/fhir">
    #{generate_id(data.id)}
    </#{resource_type}>
    """
    |> String.trim()
  end

  # Helper functions for generating XML elements
  defp generate_id(""), do: ""
  defp generate_id(nil), do: ""
  defp generate_id(id), do: "  <id value=\"#{id}\"/>"

  defp generate_active(""), do: ""
  defp generate_active(nil), do: ""
  defp generate_active(active), do: "  <active value=\"#{active}\"/>"

  defp generate_status(""), do: ""
  defp generate_status(nil), do: ""
  defp generate_status(status), do: "  <status value=\"#{status}\"/>"

  defp generate_gender(""), do: ""
  defp generate_gender(nil), do: ""
  defp generate_gender(gender), do: "  <gender value=\"#{gender}\"/>"

  defp generate_birth_date(""), do: ""
  defp generate_birth_date(nil), do: ""
  defp generate_birth_date(birth_date), do: "  <birthDate value=\"#{birth_date}\"/>"

  defp generate_names([]), do: ""
  defp generate_names(nil), do: ""
  defp generate_names(names) when is_list(names) do
    names
    |> Enum.map(&generate_name/1)
    |> Enum.join("\n")
  end

  defp generate_name(name) do
    use_attr = if name.use != "", do: " use=\"#{name.use}\"", else: ""
    given_elements = name.given
                     |> Enum.map(&"    <given value=\"#{&1}\"/>")
                     |> Enum.join("\n")

    family_element = if name.family != "", do: "    <family value=\"#{name.family}\"/>", else: ""

    """
      <name#{use_attr}>
    #{given_elements}
    #{family_element}
      </name>
    """
    |> String.trim()
  end

  defp generate_telecoms([]), do: ""
  defp generate_telecoms(nil), do: ""
  defp generate_telecoms(telecoms) when is_list(telecoms) do
    telecoms
    |> Enum.map(&generate_telecom/1)
    |> Enum.join("\n")
  end

  defp generate_telecom(telecom) do
    system_attr = if telecom.system != "", do: " system=\"#{telecom.system}\"", else: ""
    value_attr = if telecom.value != "", do: " value=\"#{telecom.value}\"", else: ""
    use_attr = if telecom.use != "", do: " use=\"#{telecom.use}\"", else: ""

    "  <telecom#{system_attr}#{value_attr}#{use_attr}/>"
  end

  defp generate_addresses([]), do: ""
  defp generate_addresses(nil), do: ""
  defp generate_addresses(addresses) when is_list(addresses) do
    addresses
    |> Enum.map(&generate_address/1)
    |> Enum.join("\n")
  end

  defp generate_address(address) do
    use_attr = if address.use != "", do: " use=\"#{address.use}\"", else: ""
    type_attr = if address.type != "", do: " type=\"#{address.type}\"", else: ""

    line_elements = address.line
                    |> Enum.map(&"    <line value=\"#{&1}\"/>")
                    |> Enum.join("\n")

    city_element = if address.city != "", do: "    <city value=\"#{address.city}\"/>", else: ""
    state_element = if address.state != "", do: "    <state value=\"#{address.state}\"/>", else: ""
    postal_element = if address.postal_code != "", do: "    <postalCode value=\"#{address.postal_code}\"/>", else: ""
    country_element = if address.country != "", do: "    <country value=\"#{address.country}\"/>", else: ""

    """
      <address#{use_attr}#{type_attr}>
    #{line_elements}
    #{city_element}
    #{state_element}
    #{postal_element}
    #{country_element}
      </address>
    """
    |> String.trim()
  end

  defp generate_code(nil), do: ""
  defp generate_code(code) do
    coding_elements = code.coding
                      |> Enum.map(&generate_coding/1)
                      |> Enum.join("\n")

    text_element = if code.text != "", do: "    <text value=\"#{code.text}\"/>", else: ""

    """
      <code>
    #{coding_elements}
    #{text_element}
      </code>
    """
    |> String.trim()
  end

  defp generate_coding(coding) do
    system_attr = if coding.system != "", do: " system=\"#{coding.system}\"", else: ""
    code_attr = if coding.code != "", do: " code=\"#{coding.code}\"", else: ""
    display_attr = if coding.display != "", do: " display=\"#{coding.display}\"", else: ""

    "    <coding#{system_attr}#{code_attr}#{display_attr}/>"
  end

  defp generate_subject_reference(nil), do: ""
  defp generate_subject_reference(subject) do
    ref_attr = if subject.reference != "", do: " reference=\"#{subject.reference}\"", else: ""
    display_element = if subject.display != "", do: "    <display value=\"#{subject.display}\"/>", else: ""

    if display_element != "" do
      """
        <subject#{ref_attr}>
      #{display_element}
        </subject>
      """
      |> String.trim()
    else
      "  <subject#{ref_attr}/>"
    end
  end

  defp generate_value(nil), do: ""
  defp generate_value(value) when is_map(value) do
    keys = Map.keys(value)
    cond do
      "value" in keys and "unit" in keys ->
        # Quantity value
        value_attr = if value.value != "", do: " value=\"#{value.value}\"", else: ""
        unit_attr = if value.unit != "", do: " unit=\"#{value.unit}\"", else: ""
        system_attr = if Map.get(value, :system, "") != "", do: " system=\"#{value.system}\"", else: ""
        code_attr = if Map.get(value, :code, "") != "", do: " code=\"#{value.code}\"", else: ""

        "  <valueQuantity#{value_attr}#{unit_attr}#{system_attr}#{code_attr}/>"

      keys == ["value"] ->
        # String value
        "  <valueString value=\"#{value.value}\"/>"

      true ->
        ""
    end
  end
end