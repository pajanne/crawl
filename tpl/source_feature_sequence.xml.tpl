<response>
    <results name="$response.name" >
    <!-- returns all the detected changes for a particular organism from a certain date  -->
    #for $sequence in $response.sequence:
        <gene 
            uniqueName="$sequence.uniqueName"
            length="$sequence.length"
            start="$sequence.start"
            end="$sequence.end"
            dna="$sequence.dna"
            />
    #end for
    </results>
</response>