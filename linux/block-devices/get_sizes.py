# license: BSD-3-Clause
# Copyright (c) 2020, Matheus Xavier Silva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from subprocess import run, DEVNULL
import json

# list all devices
devs_json = json.loads(
    run(
        ["lsblk", "--json", "-o", "NAME,RM,RO,UUID,MOUNTPOINT,TRAN"],
        capture_output=True,
    ).stdout
)
for dev in devs_json.get("blockdevices"):
    # get the size in sectors and sector size of all devices
    res = run(
        ["blockdev", "--getsize", "--getss", "--getbsz", f"/dev/{dev['name']}"],
        capture_output=True,
    )
    if res.stderr != b"":
        print(res.stderr.decode())
        exit(1)
    sizes = [bstr.decode() for bstr in res.stdout.split(b"\n") if bstr != b""]
    # calculate the sizes
    sc = int(sizes[0])
    ss = int(sizes[1])
    bs = int(sizes[2])
    bytes_sz = sc * ss
    block_ct = bytes_sz // bs
    print(
        """/dev/{devname:s} size is {sc:d} sectors, with a sector size of {ss:d}, {sc:d}*{ss:d} = {tb:d}B,
with a block size of {bs:d}B thus the device has {blkct:d} blocks or {szgib:.2f}GiB
---""".format(
            devname=dev["name"],
            sc=sc,
            ss=ss,
            bs=bs,
            tb=bytes_sz,
            blkct=block_ct,
            szgib=((block_ct * bs) / 1024 ** 3),
        )
    )
