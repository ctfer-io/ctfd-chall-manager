package main

import (
	"encoding/json"

	"github.com/ctfer-io/chall-manager/sdk"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

type Additional struct {
	Flag           string `json:"add-flag"`
	ConnectionInfo string `json:"add-connection-info"`
	VariateEnable  string `json:"add-variate-enable"`

	Ipv4 string `json:"add-ipv4"`
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

		resp.Flag = pulumi.String(additionalData.Flag).ToStringOutput()

		if additionalData.VariateEnable == "true" {
			resp.Flag = pulumi.String(sdk.Variate(req.Config.Identity, additionalData.Flag)).ToStringOutput()
		}

		resp.ConnectionInfo = pulumi.String(additionalData.ConnectionInfo).ToStringOutput()
		return nil
	})
}
