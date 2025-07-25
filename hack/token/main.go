package main

import (
	"fmt"
	"log"
	"os"

	"github.com/ctfer-io/go-ctfd/api"
)

// This utility login to a CTFd instance for acceptance testing of the provider,
// and creates an API key ready to work.

func main() {
	key := "CTFD_API_KEY"
	if k, ok := os.LookupEnv("CTFD_OUTPUT_KEY"); ok {
		key = k
	}
	url := os.Getenv("CTFD_URL")
	name := os.Getenv("CTFD_NAME")
	password := os.Getenv("CTFD_PASSWORD")

	nonce, session, err := api.GetNonceAndSession(url)
	if err != nil {
		log.Fatalf("Getting nonce and session: %s", err)
	}
	client := api.NewClient(url, nonce, session, "")

	if err := client.Login(&api.LoginParams{
		Name:     name,
		Password: password,
	}); err != nil {
		log.Fatalf("Logging in: %s", err)
	}

	// Create API Key
	token, err := client.PostTokens(&api.PostTokensParams{
		Expiration:  "2222-01-01",
		Description: "Github Workflow CI API token.",
	})
	if err != nil {
		log.Fatalf("Creating API token: %s", err)
	}

	if os.Getenv("CI") == "true" {
		ghf := os.Getenv("GITHUB_ENV")
		f, err := os.OpenFile(ghf, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
		if err != nil {
			log.Fatalf("Opening $GITHUB_ENV file (%s): %s", ghf, err)
		}
		defer f.Close()
		if _, err := f.WriteString(fmt.Sprintf("%s=%s\n", key, *token.Value)); err != nil {
			log.Fatalf("Writing %s to $GITHUB_ENV file (%s): %s", key, ghf, err)
		}

	} else {
		fmt.Printf("%s\n", *token.Value)
	}

}
