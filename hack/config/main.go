package main

import (
	"fmt"

	"github.com/ctfer-io/pulumi-ctfd/sdk/go/ctfd"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {
		conf := config.New(ctx, "")

		fmt.Print(conf.Get("url"))
		// Create provider
		provider, err := ctfd.NewProvider(ctx, "ctfd-fine-grained", &ctfd.ProviderArgs{
			//Url:    pulumi.String(conf.Get("url")), // Lookup os.Getenv by default
			//ApiKey: conf.GetSecret("api_key"), // Lookup os.Getenv by default
		})
		if err != nil {
			return err
		}

		// create 3 user
		user1, err := ctfd.NewUser(ctx, "user1", &ctfd.UserArgs{
			Name:     pulumi.String("user1"),
			Password: pulumi.String("user1"),
			Email:    pulumi.String("user1@example.com"),
		}, pulumi.Provider(provider))
		if err != nil {
			return err
		}

		user2, err := ctfd.NewUser(ctx, "user2", &ctfd.UserArgs{
			Name:     pulumi.String("user2"),
			Password: pulumi.String("user2"),
			Email:    pulumi.String("user2@example.com"),
		}, pulumi.Provider(provider), pulumi.DependsOn([]pulumi.Resource{user1}))
		if err != nil {
			return err
		}

		user3, err := ctfd.NewUser(ctx, "user3", &ctfd.UserArgs{
			Name:     pulumi.String("user3"),
			Password: pulumi.String("user3"),
			Email:    pulumi.String("user3@example.com"),
		}, pulumi.Provider(provider), pulumi.DependsOn([]pulumi.Resource{user2}))
		if err != nil {
			return err
		}

		// create 2 teams
		team1, err := ctfd.NewTeam(ctx, "team1", &ctfd.TeamArgs{
			Name:     pulumi.String("team1"),
			Password: pulumi.String("team1"),
			Email:    user1.Email,
			Captain:  user1.ID(),
			Members: pulumi.StringArray{
				user1.ID(),
				user2.ID(),
			},
		}, pulumi.Provider(provider))
		if err != nil {
			return err
		}

		_, err = ctfd.NewTeam(ctx, "team2", &ctfd.TeamArgs{
			Name:     pulumi.String("team2"),
			Password: pulumi.String("team2"),
			Email:    user3.Email,
			Captain:  user3.ID(),
			Members: pulumi.StringArray{
				user3.ID(),
			},
		}, pulumi.Provider(provider), pulumi.DependsOn([]pulumi.Resource{team1})) // force Team1 creation before
		if err != nil {
			return err
		}

		return nil
	})
}
