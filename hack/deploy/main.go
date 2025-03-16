package main

import (
	"encoding/json"

	"github.com/ctfer-io/chall-manager/sdk"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

type Additional struct {
	Flag           string `json:"add-flag"`
	ConnectionInfo string `json:"add-connection-info"`
}

func main() {
	sdk.Run(func(req *sdk.Request, resp *sdk.Response, opts ...pulumi.ResourceOption) error {
		// Convert the map to a JSON-encoded byte slice
		additionalBytes, err := json.Marshal(req.Config.Additional)
		if err != nil {
			return err
		}

		var additionalData Additional
		err = json.Unmarshal(additionalBytes, &additionalData)
		if err != nil {
			return err
		}

		if additionalData.Flag == "" {
			additionalData.Flag = "BREFCTF{Cypress_testing}"
		}

		if additionalData.ConnectionInfo == "" {
			additionalData.ConnectionInfo = "http://localhost"
		}

		resp.Flag = pulumi.String(sdk.Variate(req.Config.Identity, additionalData.Flag)).ToStringOutput()
		resp.ConnectionInfo = pulumi.String(sdk.Variate(req.Config.Identity, additionalData.ConnectionInfo)).ToStringOutput()

		return nil
	})
}
