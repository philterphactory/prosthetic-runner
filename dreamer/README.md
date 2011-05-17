# dreamer

A dreaming prosthetic.

When it's target weavr is asleep (as determined by a state call) the prosthetic
has a chance to 'dream'. This means we find a posted image from the last few days,
fetch the source image, do some simple manipulation on it, and store it locally,
then blog that image as a new Article post to the weavr's blog.
