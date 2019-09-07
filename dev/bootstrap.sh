#!/bin/bash

# Bootstrap script developers should run to set up their environments.
install_hooks()
{
    git config core.hooksPath ./dev/hooks
}

echo 'Configuring hooks...'
install_hooks
