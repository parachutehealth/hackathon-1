defmodule FhirElixir.MixProject do
  use Mix.Project

  def project do
    [
      app: :fhir_elixir,
      version: "0.1.0",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      extra_applications: [:logger],
      mod: {FhirElixir.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:sweet_xml, "~> 0.7"},
      {:ex_doc, "~> 0.31", only: :dev, runtime: false}
    ]
  end
end