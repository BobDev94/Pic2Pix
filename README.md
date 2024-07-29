# Pic2Pix
A script to process pictures/drawings of people to turn them into sprites usable in 2d game engines like GameMaker

A basic demo of what you can expect this script to do: Please note that the script expects the part to be extracted to be in the middle of the image. It samples the edges to determine the range of pixels to be filtered out, so if the edge corners are covered by the parts to be extracted, you'll have issues. 

![Capture](https://github.com/user-attachments/assets/f42106d4-6e55-43ad-862d-7c9b2c042f8d)

                   |
                   V

![Sprited](https://github.com/user-attachments/assets/d283df28-e98f-4853-8a27-423b38e56d84)

The background doesnt have to be a perfect green screen. so long as it is distinct from the target, and is somewhat uniformly colored, it will be filtered out. The target shouldnt be similar in color to the background; if it is, you'll see parts of the target parts filtered out

Try turning yourself into a sprite!

The default color palette in the code is fantasy24 on Lospec

For pencil drawings and doodles, anything with just a single color, rename your image so it has "pencil" in the name




![pencil](https://github.com/user-attachments/assets/753184c0-213a-484b-8861-07df3b8e1393)

                    |
                    V
                    
![transparency_test1](https://github.com/user-attachments/assets/a2960f1f-469b-41dd-bac9-1d35b7fd29fc)

Yes, I have the artistic ability of a drunk walrus. Hopefully, you're much better.



![zom_idle](https://github.com/user-attachments/assets/905ed294-1a87-406e-88a8-d329a1781305)


                    |
                    V



![c2pixzom_idle](https://github.com/user-attachments/assets/7fdc947f-f968-43aa-ae2f-0b85fa891124)
