import tkinter as tk
from tkinter import scrolledtext
import requests
import re
import time
import os

def initialFocusOnSearch(action):
    value = t.get('1.0', 'end-1c')
    if value == 'Input your search terms here':
        t.delete('1.0', 'end')

def removeDuplicatesMaintainOrder(seq):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (x in seen or seen_add(x))]

def clearTextInput():
    infoTextBox.configure(state='normal')
    t.delete('1.0', 'end')
    infoTextBox.delete('1.0', 'end')
    infoTextBox.configure(state='disabled')
    
def checkPath():
    if not os.path.isdir(pathInput.get()) and pathInput.get() != '':
        tk.messagebox.showerror('Path Box Error', 'Please input a valid path or leave this text box blank.')
    elif t.get('1.0', 'end-1c') == '':
        tk.messagebox.showerror('Search Box Error', 'Please input at least one search term.')
    else:
        downloadFiles()
        
def downloadFiles():  
    # URL for search endpoint
    searchURL = 'http://REDACTED.REDACTED.com:8080/SEARCH.ASP'
          
    # Reads the value(s) in the search terms text box
    searchTerms = t.get('1.0', 'end-1c').split('\n')
    searchTerms = [term for term in searchTerms if term != '']
    potentialDuplicates = searchTerms
    
    # Remove duplicate search terms and save the results to a variable
    searchTerms = removeDuplicatesMaintainOrder([line.strip() for line in searchTerms])
    lines = searchTerms
    
    # Directory where the PDF files will be saved to
    myDir = os.path.abspath(pathInput.get())
    myDir += '\\'
   
    # List of search terms which yielded no result
    notFound = []
    
    # Start reading from the first line of the text file
    searchPos = 0

    # Start counting search terms from 1
    count = 1
        
    # Start counting at the second page if the PDF is NOT found on the first page
    pgCount = 2
    
    # Where the majority of the work takes place
    for i in range(len(lines)):
        time.sleep(0.1)
        
        searchTerm = lines[searchPos]
        
        infoTextBox.configure(state='normal')
        infoTextBox.insert(tk.END,'Searching for %s...#%s\n' % (searchTerm, count))
        infoTextBox.see(tk.END)         # Scroll if necessary
        
        searchPos += 1
        
        count += 1
        
        try:
            payload = {'SearchString': searchTerm, 'Action': 'Go'}
            
            headers = {'User-Agent': 'my-app/0.0.1'}
                
            r = requests.post(searchURL, data=payload, headers=headers)
            
            cookies = r.cookies
              
            matchingPDF = f"(http.*{searchTerm}.*\.pdf)'"
            
            pdf = ''.join(set(re.findall(r"%s" % matchingPDF, r.text)))
            
            # If a match is found on the first page
            if pdf:
                secondR = requests.get(pdf)
            
                filename = myDir + searchTerm + '.pdf'
                
                with open(filename, 'wb') as f:
                    f.write(secondR.content)
                
            # If a match is NOT found on the first page, search through all remaining pages (if available)
            if not pdf:
                pageRegEx = ''.join(max(re.findall(r'NAME="pg" VALUE="(\d{1,2})"', r.text)))
                if pageRegEx:
                    found = False
                    while not found:
                        time.sleep(0.1)
			infoTextBox.configure(state='normal')
                        infoTextBox.insert(tk.END,'Searching on page %s\n' % pgCount)
                        infoTextBox.see(tk.END)         # Scroll if necessary
                        pgCount += 1
                        secondPayload = {'Advanced': '', 'pg': str(pageRegEx), 'qu': {searchTerm}, 'RankBase': '1000', 'sc': '%2F'}
                        nextPage = requests.get(searchURL, params=secondPayload, headers=headers, cookies=cookies)    
                        nextPDF = ''.join(set(re.findall(r"%s" % matchingPDF, nextPage.text)))
                        pageRegEx = ''.join(max(re.findall(r'NAME="pg" VALUE="(\d{1,2})"', nextPage.text)))
                        if nextPDF:
                            pgCount = 2
                            found = True
                            nextR = requests.get(nextPDF)
                            filename = myDir + searchTerm + '.pdf'
                            with open(filename, 'wb') as f:
                                f.write(nextR.content)
                        elif pageRegEx:
                            maxPage = re.findall(r'Page (\d{1,2}) of (\d{1,2})', nextPage.text)
                            if maxPage[0][0] == maxPage[0][1]:
                                pgCount = 2
                                found = True
                                notFound.append(searchTerm)
                            if pgCount > 10:
                                pgCount = 2
                                found = True
                                notFound.append(searchTerm)
                            continue
                else:
                    # Add the search term to the notFound list, because the pdf wasn't found on the first page and there are no other pages to search on
                    notFound.append(searchTerm)
        except:
            notFound.append(searchTerm)
            continue
        
    # Let the user know the result of the searches
    if len(notFound) == 0:
        infoTextBox.insert(tk.END,'\nAll %s of the search terms yielded a match.\n' % (len(lines)))
        infoTextBox.see(tk.END)         # Scroll if necessary
        infoTextBox.configure(state='disabled')
    else:
        infoTextBox.insert(tk.END,'\nWe could not find the following terms:')
        infoTextBox.see(tk.END)         # Scroll if necessary
        for term in notFound:
            infoTextBox.insert(tk.END, '\n%s' % term)
            infoTextBox.see(tk.END)         # Scroll if necessary
        infoTextBox.configure(state='disabled')
        
    # If there were duplicates, let the user know how many were removed
    if len(potentialDuplicates) > len(lines):
        infoTextBox.configure(state='normal')
        if len(notFound) > 0:
            infoTextBox.insert(tk.END, '\n')
        duplicateNumbers = len(potentialDuplicates) - len(lines)
        infoTextBox.insert(tk.END,'\nThere were %s duplicate search terms removed.' % duplicateNumbers)
        infoTextBox.see(tk.END)         # Scroll if necessary
        infoTextBox.configure(state='disabled')

# Instantiate the GUI window
root = tk.Tk()
root.title('MY GUI NAME')
root.geometry('800x300')
root.iconbitmap('C:\\Users\\REDACTED\\Desktop\\Documents\\Miscellaneous\\wolf2.ico')

# Create the text box for the search terms
t = scrolledtext.ScrolledText(master=root, wrap=tk.WORD, width=40, height=10)
t.grid(row=0, column=0, padx=10, pady=10)
t.insert('1.0', 'Input your search terms here')
t.bind('<FocusIn>', initialFocusOnSearch)

# Create a text box for the informational data
infoTextBox = scrolledtext.ScrolledText(master=root, wrap=tk.WORD, width=50, height=10, fg='blue')
infoTextBox.configure(state='disabled')
infoTextBox.grid(row=0, column=1)

# Create a button to clear the contents of the search terms text box and the informational data text box
clearButton = tk.Button(master=root, text='Clear the search terms', command=clearTextInput, fg='red')
clearButton.grid(row=1, column=1, sticky=tk.W, pady=2)

# Create a label for the path input box
tk.Label(master=root, text='Path to save the PDF files').grid(row=2, column=0, sticky=tk.W, pady=4)

# Create an input box for the path to save the PDF files
pathInput = tk.Entry(master=root, width=70, insertofftime=0)
pathInput.grid(row=2, column=1, sticky=tk.W, pady=4)
pathInput.focus()

# Create a label showing the user's current working directory
tk.Label(master=root, text='If you do not input a path, the PDF files will be saved to:\n%s' % os.getcwd()).grid(row=3, column=0, sticky=tk.W, pady=4)
       
# Button the user presses to run the search
myButton = tk.Button(master=root, text='Run your search', command=checkPath, fg='red')
myButton.grid(row=1, column=0, sticky=tk.W, pady=2)

# Create a label showing the author's email address
tk.Label(master=root, text='If you have any feedback, please email REDACTED@REDACTED.com').grid(row=3, column=1, sticky='sw', pady=4)

root.mainloop()
