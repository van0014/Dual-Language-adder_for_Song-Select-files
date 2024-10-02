#Simple Song Select / CCLI text file translator
#Uses DeepL translation API
#Detects song sections and adds the translation below each verse
#By Daniel van Rijthoven
import deepl, os, argparse

#Arguments:

#   --infile    <input file>
#   --outfile   <output file>
#   --lang      <2 letter language code>
#   --api       <DeepL API key>

parser = argparse.ArgumentParser()
parser.add_argument('--infile', dest='infile', type=str, help='Input file')
parser.add_argument('--outfile', dest='outfile', type=str, help='Output file')
parser.add_argument('--lang', dest='lang', type=str, help='Language. Default: Simplified Chinese. 2 letter code. Please refer to https://developers.deepl.com/docs/resources/supported-languages')
parser.add_argument('--api', dest='apikey', type=str, help='DeepL API key. (Account required, with a free plan chosen. No cost, 500,000 characters / month. Card needed for account verification purposes only)')
args = parser.parse_args()

#Input and output file variables
patha = args.infile
pathb = args.outfile

#Used to detect each song section
title = 0
space = 0
conseq = 0
fatal = 0

print("This program takes a CCLI song file")
print("and integrates translated text below each line")
print("using the DeepL translator")
print("")

#API key - Do not include in public source code. Use command line arguments instead
#Storing your API key in this section is not suitable for any public releases
if args.apikey == None:
    args.apikey = ""
    print("API key not provided. Exiting")
    fatal += 1

#Function to parse file name, path and file extension
def get_file_name(file_path):
    file_path_components = file_path.split('/')
    file_name_and_extension = file_path_components[-1].rsplit('.', 1)
    return file_name_and_extension[0]

#Check if input file exists
if args.infile == None:
    print("File not found. Exiting")
    fatal += 1

#End on critical variables missing or unuseable
if fatal >= 1:
    print("Program ended.")
    exit()

#Default language: Chinsese (Simplified)
if args.lang == None:
    args.lang = "ZH-HANS"
    print("Using default language: ",args.lang)
else:
    print("Language: ",args.lang)

#Default file path, which includes an underscore and the language code
if args.outfile == None:
    froot, fext = os.path.splitext(patha)
    pathb = os.path.dirname(patha) + os.path.splitext(os.path.basename(patha))[0] + "_" + args.lang + fext#get_file_name(args.infile + "ZH-HANS")
    args.outfile = pathb
    print("Default file name: ",os.path.splitext(os.path.basename(patha))[0] + "_" + args.lang)
else:
    froot, fext = os.path.splitext(pathb)
    print("Output file name: ",os.path.splitext(os.path.basename(pathb))[0] + fext)

#DeepL initialisation and API key
#Please make a free account with DeepL to get an API key

#Check that input file exists and output file doesn't
if os.path.isfile(patha) and not os.path.isfile(pathb):
    auth_key = args.apikey
    translator = deepl.Translator(auth_key)
    print("Begin processing file: ",os.path.splitext(os.path.basename(patha))[0])
    print("")

#Open both files, one in read mode, one in write mode
    with open(args.infile,'r') as firstfile, open(args.outfile,'w') as secondfile:
        # read content from first file, line by line
        for line in firstfile:

            #Store a marker for when the song title has been detected and the next line has been processed
            if title == 1:
                title = 2

            #Detect end of file and ignore copyright and author in the translated results
            if "©" in line:
                print("")
                print("Completed")
                exit()
            #CCLI is often found at the end of a file. End the program here
            if "CCLI" in line:
                print("")
                print("Completed")
                exit()

            #Detect empty lines. These are critical for sorting through the file
            if len(line) <= 1:
                #Record consecutive empty lines
                space += 1
                #Reset the line counter for when lines are found that have text
                conseq = 0
                print("")
            else:
                #A line of text has been found. Ignore the first line, translating only the lyrics
                space = 0
                conseq += 1
                if title == 0:
                    title = 1
                    print("Song title - ",line.strip())

            #Detect song sections, approximately. This also detects the song title
            if title >= 2 and conseq == 1:
                print(line.strip())

            #Detect the start of each song lyrics section, approximately
            if title >= 1 and conseq >= 2:
                #Translate
                result = translator.translate_text(line, target_lang=args.lang)
                #Add content to second file
                secondfile.write(line)
                secondfile.write(result.text)
                print(line.strip())
                print(result.text.strip())
            else:
                #Copy the original file
                secondfile.write(line)
else:
    #What to do if files aren't found
    if not os.path.isfile(pathb):
        print("Input file not found")
    else:
        print("Output file already exists. Please check it and delete if it's not required anymore")
