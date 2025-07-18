package main

import (
	"fmt"
	"strconv"

	"github.com/ctfer-io/chall-manager/sdk"
	"github.com/pulumi/pulumi-docker/sdk/v4/go/docker"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func main() {
	sdk.Run(func(req *sdk.Request, resp *sdk.Response, opts ...pulumi.ResourceOption) error {

		// check defaults
		image, ok := req.Config.Additional["image"]
		if !ok {
			image = "pandatix/license-lvl1:latest"
		}

		portStr, ok := req.Config.Additional["port"]
		if !ok {
			portStr = "8080"
		}

		port, err := strconv.Atoi(portStr)
		if err != nil {
			return err
		}

		hostname, ok := req.Config.Additional["hostname"]
		if !ok {
			hostname = "localhost"
		}

		protocol_port, ok := req.Config.Additional["protocol_port"]
		if !ok {
			protocol_port = "tcp"
		}

		protocol_url, ok := req.Config.Additional["protocol_url"]
		if !ok {
			protocol_url = "http"
		}

		// pull image locally
		img, err := docker.NewRemoteImage(req.Ctx, "challenge-image", &docker.RemoteImageArgs{
			Name:        pulumi.String(image),
			Platform:    pulumi.String("linux/amd64"),
			KeepLocally: pulumi.Bool(true), // do not remove image
		})
		if err != nil {
			return err
		}

		// create a container
		container, err := docker.NewContainer(req.Ctx, "challenge-container", &docker.ContainerArgs{
			Image: img.ImageId,
			Name:  pulumi.Sprintf("challenge-%s", req.Config.Identity),
			Ports: docker.ContainerPortArray{
				docker.ContainerPortArgs{
					Protocol: pulumi.String(protocol_port),
					Internal: pulumi.Int(port),
				},
			},
			Rm: pulumi.Bool(true),
		})
		if err != nil {
			return err
		}

		resp.ConnectionInfo = container.Ports.ApplyT(func(ports []docker.ContainerPort) string {
			port := ports[0].External
			url := fmt.Sprintf("%s://%s:%d", protocol_url, hostname, *port)
			return url
		}).(pulumi.StringOutput)

		return nil
	})
}
