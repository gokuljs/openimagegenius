## Stable Diffusion free image generator

This project was built as MVP to understand the landscape of image generation with Stable Diffusion.
Ultimately, after about 3 weeks of development, it was realized this is not a good product for ongoing development, for the following reasons:

1. Most people are instead interested in running Stable Diffusion quickly and cheaply.
2. In the cloud, you cannot do it cheaply and quickly, e.g, you need to over-provision GPU resources which are expensive.
3. Many people execute it locally, and a wide range of open source repositories have emerged. Anyone that owns a GPU with about 4GB of RAM can use a fork of the stable diffusion web UI to run it locally. 

This was nonetheless a very interesting project to develop, which provided good experience in many ways.

If you're interested, you can see the original system design and planning here:

https://pacific-drip-6f9.notion.site/Openimagegenius-f5eda2bd24b745a9a38f7124327fa08e


## The Playground

You can also access the playground to use AWS Lambda to generate images (at low quality, currently 12 inference steps):

https://auth.openimagegenius.com/

The UI is very raw, and is just a Google OAuth screen:
![image](https://user-images.githubusercontent.com/5386983/190959657-6b6ea360-edcd-48b3-ab5b-0ff751940dff.png)

It requires you to share your e-mail address.

Generating the first image takes about 3 minutes. The following will take between 1-2 minutes. They will be stored in a public S3 bucket that is behind a CloudFront / and Route 53 subdomain.
![image](https://user-images.githubusercontent.com/5386983/190960033-3cf449db-4d7f-4ace-bd49-e06115afaaaa.png)

If you think this project is worth continuing or forking, feel free to get in touch :)
