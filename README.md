Write, in Elixir, a library to serve 

Examples to keep in mind: 
https://github.com/inferno-framework/fhir_models
https://idyllic.co/implementing-fhir-with-ruby-on-rails/


ruby equivalent to keep in mind:
```ruby
xml = File.read('patient-example.xml')
patient = FHIR.from_contents(xml)
puts patient.to_xml
```