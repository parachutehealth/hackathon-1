defmodule FhirElixir.Application do
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Add any supervised processes here
    ]

    opts = [strategy: :one_for_one, name: FhirElixir.Supervisor]
    Supervisor.start_link(children, opts)
  end
end