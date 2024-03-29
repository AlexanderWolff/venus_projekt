import numpy as np
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.dates

import ipywidgets as widgets
from IPython.display import clear_output

import classes
import IO

def get_orbit(specData, orbit_number=2996):

    # current frame (orbit)
    n = str(orbit_number)
                
    frame = {'IMA': specData[n]['IMA']['spec'],
             'ELS': specData[n]['ELS']['spec'],
             'MAG': specData[n]['MAG']['spec']}

    t = {'IMA': specData[n]['IMA']['timeDt'],
         'ELS': specData[n]['ELS']['timeDt'],
         'MAG': specData[n]['MAG']['timeDt']}


    return (frame, t)

def check_validity(frame, t):

    # initialise
    ima = True
    els = True
    mag = True

    # check size of ion mass analyser data
    if len(frame['IMA']) == 0:
        ima = False
    if len(t['IMA']) == 0:
        ima = False

    # check size of electron spectrometer data
    if len(frame['ELS']) == 0:
        els = False
    if len(t['ELS']) == 0:
        els = False
        
    # check size of magnetometer data
    if len(frame['MAG']) == 0:
        mag = False
    if len(t['MAG']) == 0:
        mag = False


    # check validity of ion mass analyser data
    if ima:
        if len(frame['IMA'].data)==np.size(frame['IMA'].data):
            ima = False

    # check validity of magnetometer data
    if mag:
        for axis in ['x', 'y', 'z']:
            x = list(frame['MAG'][axis])

            if contains_data(x)==False:
                mag = False


    return (ima, els, mag)


def plot_data(frame, t, ylimits, xsize=9, ysize=6, valid=0):

    if valid == 0:
        valid = check_validity(frame,t)

    # check that the data is valid
    ima,els,mag = valid

    # create colormap type plot
    cmap = plt.cm.jet
    cmap.set_under(cmap(0))
    cmap.set_bad(cmap(0))

    fig, axes = plt.subplots(3, 1, figsize=(xsize, ysize), sharex=True, num='Instrument Data')

    for axis in axes:
        axis.clear()

    # assign subplots
    axisIMA = axes[0]
    axisELS = axes[1]
    axisMAG = axes[2]
    fig.patch.set_facecolor('white')

    # plot ion mass analyser
    if ima:
        axisIMA.set_ylabel('IMA\nion mass analyser')
        axisIMA.pcolormesh(t['IMA'], np.arange(ylimits['IMA'][1])[::-1], np.log10(frame['IMA'].clip(1e-5)), cmap='bwr', norm=colors.LogNorm())
        
        # set graphical limits
        axisIMA.set_ylim(ylimits['IMA'])
        axisIMA.set_xlim(t['IMA'][0], t['IMA'][-1])

    # plot electron spectrometer
    if els:
        axisELS.set_ylabel('ELS\nelectron spectrometer')
        axisELS.pcolormesh(t['ELS'], np.arange(ylimits['ELS'][1])[::-1], np.log10(frame['ELS'].clip(1e-5)), cmap='coolwarm', norm=colors.LogNorm())
        
        # set graphical limits
        axisELS.set_ylim(ylimits['ELS'])
        axisELS.set_xlim(t['ELS'][0], t['ELS'][-1])
        
    # plot magnetometer
    if mag:
        axisMAG.set_ylabel('MAG\nmagnetometer')
        
        magnitude = np.sqrt(frame['MAG']['z']**2+frame['MAG']['y']**2+frame['MAG']['x']**2)
        axisMAG.plot(t['MAG'], magnitude, 'k', label='magnitude')
        
        axisMAG.plot(t['MAG'], frame['MAG']['x'], 'b', label='Bx')
        axisMAG.plot(t['MAG'], frame['MAG']['y'], 'r', label='By')
        axisMAG.plot(t['MAG'], frame['MAG']['z'], 'g', label='Bz')


        # Shrink current axis's height by 10% on the bottom
        box = axisMAG.get_position()
        axisMAG.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

        # Put a legend below current axis
        axisMAG.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=4, fancybox=True, shadow=True)

        # set graphical limits
        axisMAG.set_ylim(ylimits['MAG'])
        axisMAG.set_xlim(t['MAG'][0], t['MAG'][-1])
        
    axis = {'IMA': axisIMA, 'ELS': axisELS, 'MAG': axisMAG}
    return (fig, axis)

def plot_bound(axis, bound, orbit_number):

    n = str(orbit_number)

    # color scheme
    boundColor = {'bowShock': 'r', 'IMB': '#f91ccf'}


    for b in bound[n]:
        for i in np.arange(4):
            axis['IMA'].plot([bound[n][b]['timeDt'][i], bound[n][b]['timeDt'][i]], ylimits['IMA'], c=boundColor[b], lw=2)
            axis['ELS'].plot([bound[n][b]['timeDt'][i], bound[n][b]['timeDt'][i]], ylimits['ELS'], c=boundColor[b], lw=2)
            axis['MAG'].plot([bound[n][b]['timeDt'][i], bound[n][b]['timeDt'][i]], ylimits['MAG'], c=boundColor[b], lw=2)
        
        
    # selected type of boundary
    boundType = 'bowShock'
    boundQual = None
    boundInd = 0
        
    boundQual = bound[n][boundType]['flag'][boundInd]


def plot_all_axes(axis, value, style='k--'):

    X = matplotlib.dates.date2num(value)

    ylimits = {'IMA': [0, 96], 'ELS' : [0, 128], 'MAG': [-40, 40]}

    axis['IMA'].plot([X, X], ylimits['IMA'], style, lw=2)
    axis['ELS'].plot([X, X], ylimits['ELS'], style, lw=2)
    axis['MAG'].plot([X, X], ylimits['MAG'], style, lw=2)


def onclick(event, fig, axis, i, n, region):
 
    X = event.xdata
   
    # plot lines (remove previous lines)
    try:
        for _ in range(len(region.get_orbit_values(n.get_mapping()))+1):
            axis['IMA'].lines.remove(axis['IMA'].lines[-1])
            axis['ELS'].lines.remove(axis['ELS'].lines[-1])
            axis['MAG'].lines.remove(axis['MAG'].lines[-1])
         
    except:
        try:
            axis['IMA'].lines.remove(axis['IMA'].lines[-1])
            axis['ELS'].lines.remove(axis['ELS'].lines[-1])
            axis['MAG'].lines.remove(axis['MAG'].lines[-1])
        except:
            pass
         
    if i.get_mapping() == None:
         
        if event.button == 1:
            style = 'k--'
             
        elif event.button == 3:
            style = 'k-'
             
        else:
            style = 'k-.'
         
        plot_all_axes(axis,matplotlib.dates.num2date(X), style=style)
    else:
         
        # add (left click)
        if event.button == 1:
            date = matplotlib.dates.num2date(X)
            region.add(n.get_mapping(),i.get_mapping(),date)
        # remove (right click)
        elif event.button == 3:
            region.del_entry(n.get_mapping(), i.get_mapping())
         
    styles = ['m--','m-','g--','g-','c--','c-','y--','y-']
    for (value, bound) in region.get_orbit_values_pair(n.get_mapping()):
         
        k = find_boundary_type(bound)
        plot_all_axes(axis,value,style=styles[k])

     # update
    fig.canvas.draw()
    fig.canvas.flush_events()
     
def plot_orbit(data, ylimits, n, region, xsize=9, ysize=6):

    index = n.get()
    plt.close()
    clear_output()

    try:
        if n.get_mapping() == None:
            raise Exception('no data to plot')
        
        frame, t = get_orbit(data, n.get_mapping())
        fig, axis = plot_data(frame, t, ylimits, xsize, ysize)
        
    except:
        fig, axis = plt.subplots(3, 1, figsize=(xsize, ysize), sharex=True, num='no data to display')
        
        
        
    fig, i = reset_interactivity(fig, axis, n, region)

    styles = ['m--','m-','g--','g-','c--','c-','y--','y-']
    try:
        for (value, bound) in region.get_orbit_values_pair(n.get_mapping()):
            k = find_boundary_type(bound)
            plot_all_axes(axis,value,style=styles[k])
    except:
        styles = None

    fig.suptitle('Orbit {} ({})'.format(n.get_mapping(), i.get_mapping()))

    fig.canvas.draw()
    plt.show()

    return (fig, axis, i)

def prev_orbit(event, data, ylimits, i,n,region):

    n.decrement()
    fig, axis, i = plot_orbit(data, ylimits, n, region)

    define_GUI(data,ylimits,i,n,region,fig,axis)

def next_orbit(event, data, ylimits, i,n,region):
 
     n.increment()
     fig, axis, i = plot_orbit(data, ylimits, n, region)

     define_GUI(data,ylimits,i,n,region,fig,axis)
     
def find_orbit(data, orbit_number):

    index = (orbit_number == np.array(sorted(data)).astype(int)).argmax()

    return index
    
def get_orbits(data):

    orbits = list(np.array(sorted(data)).astype(int))
     
    return orbits

def next_bound(event, i, n, fig):
    i.increment()

    fig.suptitle('Orbit {} ({})'.format(n.get_mapping(), i.get_mapping()))
    
def prev_bound(event, i, n, fig):
    i.decrement()

    fig.suptitle('Orbit {} ({})'.format(n.get_mapping(), i.get_mapping()))

def define_GUI(data, ylimits,i,n,region,fig,axis):

    # define interactivity
    button = dict()
    button['next orbit'] = widgets.Button(description="next orbit")
    button['prev orbit'] = widgets.Button(description="prev orbit")

    button['next bound'] = widgets.Button(description="next bound")
    button['prev bound'] = widgets.Button(description="prev bound")

    button['del bound'] = widgets.Button(description="del bound")

    button['next orbit'].on_click(lambda event : next_orbit(event, data, ylimits, i, n, region) )
    button['prev orbit'].on_click(lambda event : prev_orbit(event, data, ylimits, i, n, region) )

    button['next bound'].on_click(lambda event : next_bound(event, i, n, fig) )
    button['prev bound'].on_click(lambda event : prev_bound(event, i, n, fig) )

    comment = list()
    comment.append( widgets.Text(value='',placeholder='update comment',description='',disabled=False) )


    try:
        value = region.get_value(n.get_mapping(), 'comment')
        comment.append( widgets.Textarea(value=value,placeholder='no comment',description='',disabled=True) )
    except:
        comment.append( widgets.Textarea(value='',placeholder='no comment',description='',disabled=True) )

    def callback(_, comment, region, n):

        region.add(n.get_mapping(),'comment',comment[0].value)

        comment[1].value = comment[0].value
        comment[0].value = ''


    comment[0].on_submit(lambda event : callback(event, comment, region, n))

    display(widgets.VBox([
        widgets.HBox([button['prev orbit'], button['next orbit']]),

        widgets.HBox([button['prev bound'], button['next bound']]),
        
        comment[0], comment[1]
    ]))

def generate_boundary_types():
    types = ['inbound', 'outbound']
    status = ['pre', 'post']
    boundaries = ['bow shock', 'ion composition boundary']
    b = ["{} {} {}".format(i,j,k) for i in types for j in status for k in boundaries]
    b = [b[0],b[2],b[1],b[3],b[5],b[7],b[4],b[6]]

    return b

def find_boundary_type(target):
    for i, bound in enumerate(generate_boundary_types()):
        if bound == target:
            return i
        else:
            continue
            
    return None

def reset_interactivity(fig, axis, n, region):

    b = generate_boundary_types()

    i = classes.Iterator()
    i.set_min(0)
    i.set_max(len(b))
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, fig, axis, i, n, region) )

    i.set_mapping(b)
    i.decrement()

    return (fig, i)

def contains_data(x):
    return 0!=max([xx if abs(xx)>0 else 0 for i,xx in enumerate(x) ])
    
def plot_all_orbits(data, filepath='/Users/alexanderwolff/Documents/Venus_Project/graphs/', filename='orbit'):
    orbits = get_orbits(data)

    for i, orbit in enumerate(orbits):
        try:
            fig, axis = plot_orbit(data, ylimits, i, xsize=18, ysize=12)
            fig.savefig('{}{}_{}.png'.format(filepath, filename, orbit))
        except:
            print("ERROR at {} : {}".format(orbit, i))
            
            
def main(datafile='processed_data/venus_specData.npy', regionfile='data', orbitfile='orbits'):

    # load region data
    region = None
    try:
        region = IO.read_file(filename=regionfile)
    except:
        region = classes.Region()

    # load instrument data
    data = IO.get_data(datafile)
    orbits = get_orbits(data)

    #orbit file, as list
    orbits = IO.read_file(filename=orbitfile)

    orbit_number = orbits[0]
    n = classes.Iterator()
    n.set_min( 0 )
    n.set_max( len(orbits) )

    # index of current frame
    index = find_orbit(data, orbit_number)
    n.set(index)

    n.set_mapping(orbits)

    frame, t = get_orbit(data, n.get_mapping())
    ima, els, mag = check_validity(frame,t)


    # plot initial data
    ylimits = {'IMA': [0, 96], 'ELS' : [0, 128], 'MAG': [-40, 40]}

    fig, axis, i = plot_orbit(data, ylimits, n, region, xsize=9, ysize=6)

    fig.suptitle('Orbit {} ({})'.format(n.get_mapping(), i.get_mapping()))

    define_GUI(data,ylimits,i,n,region,fig,axis)
