#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      v.divide.training_validation
# AUTHOR(S):   Anika Bettge
#
# PURPOSE:     Divides data into training and validation data
# COPYRIGHT:   (C) 2019 by Hajar Benelcadi and Anika Bettge, mundialis
#
#              This program is free software under the GNU General Public
#              License (>=v2). Read the file COPYING that comes with GRASS
#              for details.
#
#############################################################################
#%module
#% description: divides data into training and validation data.
#% keyword: vector
#% keyword: sampling
#% keyword: statistics
#% keyword: random
#% keyword: stratified random sampling
#%end

#%option G_OPT_V_INPUT
#%end

#%option G_OPT_DB_COLUMN
#% description: Name of column with class information
#%end

#%option G_OPT_V_OUTPUT
#% key: training
#%end

#%option G_OPT_V_OUTPUT
#% key: validation
#%end

#%option
#% key: training_percent
#% type: integer
#% required: no
#% description: Percent of data which should be selected as training data
#% answer: 30
#%end

from grass.script import core as grass
import os
import random


def cleanup(rm_vectors):
    grass.message(_("Cleaning up..."))
    nuldev = open(os.devnull, 'w')
    for rm_v in rm_vectors:
        grass.run_command(
            'g.remove', flags='f', type='vector', name=rm_v, quiet=True, stderr=nuldev)


def main():
    input = options['input']
    column = options['column']
    training = options['training']
    validation = options['validation']
    training_percent = options['training_percent']

    # get classes
    grass.message("Getting classes...")
    classes = grass.parse_command(
        'v.db.select', map=input,
        column=column, flags='c')

    grass.message("Select point for each class...")
    training_cats = []
    validation_cats = []
    for cl in classes:
        where_str = "%s = '%s'" % (column, cl)
        classI = grass.parse_command(
            'v.db.select', map=input, columns='cat',
            flags='c', where=where_str)
        cats_classI = [x for x in classI]
        random.shuffle(cats_classI)
        num_classI = len(cats_classI)
        num_trainingdata = round(int(training_percent) / 100.0 * num_classI)
        cats_tr = cats_classI[:num_trainingdata]
        cats_val = cats_classI[num_trainingdata:]
        training_cats.extend(cats_tr)
        validation_cats.extend(cats_val)

    grass.message("Extract training and validation points...")
    grass.run_command(
        'v.extract', input=input, cats=','.join(training_cats), output=training)
    grass.run_command(
        'v.extract', input=input, cats=','.join(validation_cats), output=validation)

    grass.message("Divided data in <%s> and <%s>" % (training, validation))


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
