## **RC Beam Analysis and Design**

- Before design, the app ask to execute beam analysis feature, it will display shear force diagram(SFD) and bending moment diagram(BMD), it's value use for design reinforcements.
- If you aready have Mu, Vu you can skip analysis part
- The deflection use ChatGPT code by cubic interpolation method and remain under developing.


### Instructions

1. Install Python, Git, Anaconda, and VSCode

- [Python](https://www.python.org/downloads/)
- [Git](https://github.com/git-guides/install-git)
- [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
- [VSCode](https://code.visualstudio.com/download)

2. Go to your project directory

```
cd <your project folder path>
```

3. Clone this repository

```
git clone https://github.com/Suzanoo/beam.git
```

4. Create conda env and activate it

```
 conda create --name <your conda env name> python=3.xxx
 conda activate <your conda env name>
```

5. Install dependency via requirements.txt

```
pip install -r requirements.txt
```

6. Enjoy !!
```
python app/beam_design.py --b=40 --h=60
python app/deep_beam.py --b=40 --h=100 --l=5
python app/teebeam.py --bw=30 --b=100 --hf=10 --h=40 --l=4 --Mu=85 --Vu=120 --Tu=12

Look at FLAGS definition for alternative
```

Feedback : highwaynumber12@gmail.com
