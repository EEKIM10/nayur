<div style="text-align: center">
<h1 align="center">Nayur</h1>
<i align="center">The least helpful AUR helper</i>
</div>

------

Have you ever used [yay](https://aur.archlinux.org/packages/yay)? Or similar AUR helpers?

Have you ever thought "Man, these AUR helpers make life so easy"?
Have you ever then followed that thought up with "I love AUR helpers, they just work and do it all for me?"

No you haven't! Anyway, lets pretend you have.

**Nayur is here to change that!**

*Nayur* comes packed with helpful features and tools, such as

* The least intuitive command line
* Super tedeous AUR interactions
* The least useful output (and also super quiet, as per the demands of [@Nicroxio](https://github.com/Nicroxio))
* A lack of useful error messages
* Missing half of the functionality you actually want
* A lack of documentation
* No standard pacman wrapping (like yay does)

And a painful amount more!

What are you waiting for? Install Nayur now!

## Installation

You can install via pipx (I might put this on the AUR later for shits and giggles)

```shell
$ python3 -m pip install pipx
$ pipx install nayur
$ pipx ensurepath
$ nayur --help
```

## Usage

HAHAHAHAHAH GOOD LUCK BOZO

<details>
<summary>Actual usage guide if you're a bit stupid (dumbasses only)</summary>

```shell
# Find an AUR package
$ nayur search <query>

# Get an AUR package
$ nayur cache get <package (full name)>

# Prepare that package for installation
$ nayur build <package (full name)>

# Install that package
$ nayur install <package (full name)>

# Update the package (in cache anyway)
$ nayur cache update <package (full name)>

# List cached packages
$ nayur cache list

# Remove a cached package
$ nayur cache remove <package (full name)>

# Or clear the entire cache
$ nayur cache clear
```

Also, if you actually want marginally more information on why an issue may have occured, you can run nayur with
`--debug`, and/or `--log-level DEBUG` (logs are spat into `$HOME/.cache/nayur/nayur.log`)

For example:
```shell
$ nayur --debug cache get horizontallyspinningrat
# or
$ nayur --log-level DEBUG cache get horizontallyspinningrat
# or even
$ nayur --debug --log-level DEBUG cache get horizontallyspinningrat
```
</details>

## Contributing
If you actually want to contribute to this shitshow, you can open an issue or PR, either works.
Just remember that this program is a *functional joke* - it's meant to be funny and barely functional.

**Do not take this project seriously**

## License
[Can be found here (I will absolutely sue your ass with the best lawyers in the world if you violate this)](/LICENSE)
