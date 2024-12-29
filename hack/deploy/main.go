package main

import (
	"github.com/ctfer-io/chall-manager/sdk"
	"github.com/pulumi/pulumi-random/sdk/v4/go/random"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {
		// 1. Load config
		cfg := config.New(ctx, "prebuilt")
		config := map[string]string{
			"identity": cfg.Get("identity"),
		}

		// 2. Create resources
		_, err := random.NewRandomString(ctx, "random", &random.RandomStringArgs{
			Length: pulumi.Int(len(config["identity"])),
		})
		if err != nil {
			return err
		}

		// 3. Export outputs
		ctx.Export("connection_info", pulumi.Sprintf("curl https://%s.brefctf.ctfer.io", config["identity"]))
		ctx.Export("flag", pulumi.String(sdk.Variate(config["identity"], "BREFCTF{Cypress_testing}")))

		return nil
	})
}
